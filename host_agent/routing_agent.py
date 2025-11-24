# pylint: disable=logging-fstring-interpolation
import asyncio
import json
import os
import uuid
from typing import Any, Optional, List, Tuple
from datetime import datetime
from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from remote_agent_connection import (
    # RemoteAgentConnections,
    TaskUpdateCallback,
)

from routing_remote_agent_connection import RemoteAgentConnections
from registry_client import RegistryClient
from registry_models import RegistryListReq, RegistryListResp

load_dotenv()


def convert_part(part: Part, tool_context: ToolContext):
    """Convert a part to text. Only text parts are supported."""
    if part.type == 'text':
        return part.text

    return f'Unknown type: {part.type}'


def convert_parts(parts: list[Part], tool_context: ToolContext):
    """Convert parts to text."""
    rval = []
    for p in parts:
        rval.append(convert_part(p, tool_context))
    return rval


def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {
        'message': {
            'role': 'user',
            'parts': [{'type': 'text', 'text': text}],
            'messageId': uuid.uuid4().hex,
        },
    }

    if task_id:
        payload['message']['taskId'] = task_id

    if context_id:
        payload['message']['contextId'] = context_id
    return payload


class RoutingAgent:
    """The Routing agent.

    This is the agent responsible for choosing which remote seller agents to send
    tasks to and coordinate their work.
    """

    def __init__(
        self,
        registry_base_url: Optional[str] = None,
        task_callback: TaskUpdateCallback | None = None,
    ):
        # self.task_callback = task_callback
        # self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        # self.cards: dict[str, AgentCard] = {}
        # self.agents: str = ''
        registry_url = registry_base_url or os.getenv("REGISTRY_BASE_URL", "http://localhost:8000")
        print(f"\n📡 Initializing RoutingAgent with Registry URL: {registry_url}")
        print(f"   To change, set REGISTRY_BASE_URL environment variable.\n")
        
        self.registry = RegistryClient(
            registry_url,
            timeout=60.0  # 增加超时时间
        )
        self._connections: dict[str, RemoteAgentConnections] = {}

    # -------- 路由：调 Registry 并构造直连连接 --------
    async def resolve_client(
        self, keyword: str, task: str, top_k: int
    ) -> Tuple[List[Tuple[str, str]], List[dict]]:
        """
        调用 Registry，按 score 降序选取前 k 个候选，
        返回:
            results: [(agent_name, url)]
            agents_clean: 去掉 score / agent_id 的完整 agent 信息
        """
        # === 构造请求（纯字典） ===
        req = {
            "request_id": f"req-{uuid.uuid4()}",
            "task": task,
            "top_k": top_k,
        }

        resp = None
        resp: RegistryListResp = await self.registry.list_agents(keyword, req)
        # === 验证响应 ===
        if resp.status != "success" or not resp.agents:
            raise LookupError(
                f"No agent candidates for keyword='{keyword}', task='{task[:80]}...'"
            )

        # === 按分数降序排序 ===
        # resp.agents 是 List[RegistryAgentItem]（Pydantic 模型）
        agents_sorted = sorted(resp.agents, key=lambda a: a.score, reverse=True)

        # === 限制 top_k ===
        count = len(agents_sorted)
        k = min(top_k, count) if count > 0 else 0
        if k == 0:
            raise LookupError("No valid candidates after sorting.")

        # === 构造 results [(name, url)] ===
        results: List[Tuple[str, str]] = []
        for item in agents_sorted[:k]:
            results.append((item.name, item.url))
            self._connections[item.name] = item.url

        # === 构造 agents_clean（去掉 score 和 agent_id），但保留其他字段 ===
        agents_clean: List[dict] = []
        for agent in agents_sorted[:k]:
            clean = agent.model_dump(exclude={"agent_id"})
            agents_clean.append(clean)

        return results, agents_clean


    # -------- 入口：路由 + 发送消息 + 解析 --------
    async def send_message_to_agent(
            self,
            keyword: str,
            task: str,
            tool_context: ToolContext,
            top_k: int = 3,
    ) -> Optional[Task]:
        """
        先路由（取 Top-k），再按得分从高到低依次直连 /messages。
        返回第一个成功的 Task；若都失败，返回 None（并在异常中提供聚合信息也可选）。
        """
        state = tool_context.state

        # 1) 路由：拿前 k 个候选
        candidates = await self.resolve_client(keyword=keyword, task=task, top_k=top_k)

        # 2) 固定一次 context_id（多次重试保持同一会话）
        context_id = state.get("context_id") or str(uuid.uuid4())
        state["context_id"] = context_id

        input_meta = state.get("input_message_metadata") or {}

        # 3) 逐个候选尝试发送
        errors: list[str] = []
        for agent_name, connection in candidates:
            state["active_agent"] = agent_name
            message_id = input_meta.get("message_id") or uuid.uuid4().hex

            payload: dict[str, Any] = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": task}],
                    "messageId": message_id,
                    "contextId": context_id,
                    # "metadata": input_meta,  # 远端支持时再打开
                }
            }

            message_request = SendMessageRequest(
                id=message_id, params=MessageSendParams.model_validate(payload)
            )

            try:
                send_response: SendMessageResponse = await connection.send_message(message_request)
            except Exception as e:
                errors.append(f"{agent_name}: request failed ({e})")
                continue

            # 校验 A2A 响应
            if not isinstance(send_response.root, SendMessageSuccessResponse):
                errors.append(f"{agent_name}: non-success response")
                continue
            if not isinstance(send_response.root.result, Task):
                errors.append(f"{agent_name}: success wrapper but no Task")
                continue

            #  首个成功即返回
            return send_response.root.result

        # 所有候选都失败
        # print 或 log 一下便于排查
        if errors:
            print("All candidates failed:\n" + "\n".join(errors))
        return None


#     async def _async_init_components(
#         self, remote_agent_addresses: list[str]
#     ) -> None:
#         """Asynchronous part of initialization."""
#         # Use a single httpx.AsyncClient for all card resolutions for efficiency
#         # Increase timeout to 300 seconds (5 minutes) for agent card resolution
#         async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
#             for address in remote_agent_addresses:
#                 card_resolver = A2ACardResolver(
#                     client, address
#                 )  # Constructor is sync
#                 try:
#                     card = (
#                         await card_resolver.get_agent_card()
#                     )  # get_agent_card is async

#                     remote_connection = RemoteAgentConnections(
#                         agent_card=card, agent_url=address
#                     )
#                     self.remote_agent_connections[card.name] = remote_connection
#                     self.cards[card.name] = card
#                 except httpx.ConnectError as e:
#                     print(
#                         f'ERROR: Failed to get agent card from {address}: {e}'
#                     )
#                 except Exception as e:  # Catch other potential errors
#                     print(
#                         f'ERROR: Failed to initialize connection for {address}: {e}'
#                     )

#         # Populate self.agents using the logic from original __init__ (via list_remote_agents)
#         agent_info = []
#         for agent_detail_dict in self.list_remote_agents():
#             agent_info.append(json.dumps(agent_detail_dict))
#         self.agents = '\n'.join(agent_info)

#     @classmethod
#     async def create(
#         cls,
#         remote_agent_addresses: list[str],
#         task_callback: TaskUpdateCallback | None = None,
#     ) -> 'RoutingAgent':
#         """Create and asynchronously initialize an instance of the RoutingAgent."""
#         instance = cls(task_callback)
#         await instance._async_init_components(remote_agent_addresses)
#         return instance

#     def create_agent(self) -> Agent:
#         """Create an instance of the RoutingAgent."""
#         return LlmAgent(
#             model='gemini-2.5-flash',
#             name='Routing_agent',
#             instruction=self.root_instruction,
#             before_model_callback=self.before_model_callback,
#             description=(
#                 'This Routing agent orchestrates the decomposition of the user asking for weather forecast, airbnb accommodation, or tripadvisor searches'
#             ),
#             tools=[
#                 self.send_message,
#             ],
#             # planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(include_thoughts=True)),
#             output_key="results"
#         )

#     def root_instruction(self, context: ReadonlyContext) -> str:
#         """Generate the root instruction for the RoutingAgent."""
#         current_agent = self.check_active_agent(context)
#         plan = context.state.get('plan', 'No plan available.')
        
#         return f"""
#         **IMPORTANT CONTEXT:**
#         - Today's date is: {datetime.now().strftime("%A, %B %d, %Y")}
#         - Use this date to interpret relative time expressions like "this weekend", "next week", "tomorrow", etc.
#         - When delegating tasks involving dates, always provide specific dates based on today's date

#         **Role:** You are an expert Routing Delegator. Your primary function is to accurately delegate user inquiries based on the provided plan to the appropriate specialized remote agents.

#         **Plan to Execute:**
#         {plan}

#         **Core Directives:**

#         * **Task Delegation:** Utilize the `send_message` function to assign actionable tasks to remote agents.
#         * **Contextual Awareness for Remote Agents:** If a remote agent repeatedly requests user confirmation, assume it lacks access to the         full conversation history. In such cases, enrich the task description with all necessary contextual information relevant to that         specific agent.
#         * **Autonomous Agent Engagement:** Never seek user permission before engaging with remote agents. If multiple agents are required to         fulfill a request, connect with them directly without requesting user preference or confirmation.
#         * **Transparent Communication:** Always present the complete and detailed response from the remote agent to the user.
#         * **User Confirmation Relay:** If a remote agent asks for confirmation, and the user has not already provided it, relay this         confirmation request to the user.
#         * **Focused Information Sharing:** Provide remote agents with only relevant contextual information. Avoid extraneous details.
#         * **No Redundant Confirmations:** Do not ask remote agents for confirmation of information or actions.
#         * **CRITICAL - Always Present Complete Agent Responses:** When you receive a response from a remote agent, you MUST present it EXACTLY and COMPLETELY to the user without any filtering, rejection, or modification. Even if you think the response might be incomplete or could be improved, present what the agent returned. Your role is to relay information faithfully, not to judge its quality or completeness. Trust that specialized agents know their domain.
#         * **Prioritize Recent Interaction:** Focus primarily on the most recent parts of the conversation when processing requests.
#         * **Active Agent Prioritization:** If an active agent is already engaged, route subsequent related requests to that agent using the         appropriate task update tool.

#         **Agent Roster:**

#         * Available Agents: `{self.agents}`
#         * Currently Active Seller Agent: `{current_agent['active_agent']}`
#                 """

#     def check_active_agent(self, context: ReadonlyContext):
#         state = context.state
#         if (
#             'session_id' in state
#             and 'session_active' in state
#             and state['session_active']
#             and 'active_agent' in state
#         ):
#             return {'active_agent': f'{state["active_agent"]}'}
#         return {'active_agent': 'None'}

#     def before_model_callback(
#         self, callback_context: CallbackContext, llm_request
#     ):
#         state = callback_context.state
#         if 'session_active' not in state or not state['session_active']:
#             if 'session_id' not in state:
#                 state['session_id'] = str(uuid.uuid4())
#             state['session_active'] = True

#     def list_remote_agents(self):
#         """List the available remote agents you can use to delegate the task."""
#         if not self.cards:
#             return []

#         remote_agent_info = []
#         for card in self.cards.values():
#             print(f'Found agent card: {card.model_dump(exclude_none=True)}')
#             print('=' * 100)
#             remote_agent_info.append(
#                 {'name': card.name, 'description': card.description}
#             )
#         return remote_agent_info

#     async def send_message(
#         self, agent_name: str, task: str, tool_context: ToolContext
#     ):
#         """Sends a task to remote seller agent.

#         This will send a message to the remote agent named agent_name.

#         Args:
#             agent_name: The name of the agent to send the task to.
#             task: The comprehensive conversation context summary
#                 and goal to be achieved regarding user inquiry and purchase request.
#             tool_context: The tool context this method runs in.

#         Yields:
#             A dictionary of JSON data.
#         """
#         if agent_name not in self.remote_agent_connections:
#             raise ValueError(f'Agent {agent_name} not found')
#         state = tool_context.state
#         state['active_agent'] = agent_name
#         client = self.remote_agent_connections[agent_name]

#         if not client:
#             raise ValueError(f'Client not available for {agent_name}')
#         # task_id = state['task_id'] if 'task_id' in state else str(uuid.uuid4())

#         if 'context_id' in state:
#             context_id = state['context_id']
#         else:
#             context_id = str(uuid.uuid4())

#         message_id = ''
#         metadata = {}
#         if 'input_message_metadata' in state:
#             metadata.update(**state['input_message_metadata'])
#             if 'message_id' in state['input_message_metadata']:
#                 message_id = state['input_message_metadata']['message_id']
#         if not message_id:
#             message_id = str(uuid.uuid4())

#         payload = {
#             'message': {
#                 'role': 'user',
#                 'parts': [
#                     {'type': 'text', 'text': task}
#                 ],  # Use the 'task' argument here
#                 'messageId': message_id,
#             },
#         }
        
#         # Don't send taskId to remote agents - let them create their own tasks
#         # Remote agents should create new tasks, not try to find existing unknown task IDs

#         if context_id:
#             payload['message']['contextId'] = context_id

#         # Add a delay to avoid hitting rate limits (429 Resource Exhausted)
#         # This helps when multiple agents are called in sequence or parallel
#         print(f"⏳ Throttling: Waiting 5 seconds before sending message to {agent_name}...")
#         await asyncio.sleep(5)

#         message_request = SendMessageRequest(
#             id=message_id, params=MessageSendParams.model_validate(payload)
#         )
#         send_response: SendMessageResponse = await client.send_message(
#             message_request=message_request
#         )
#         # Skip printing response to avoid encoding errors on Windows
#         # print('send_response', send_response.model_dump_json(exclude_none=True, indent=2))

#         if not isinstance(send_response.root, SendMessageSuccessResponse):
#             print('received non-success response. Aborting get task ')
#             return None

#         if not isinstance(send_response.root.result, Task):
#             print('received non-task response. Aborting get task ')
#             return None

#         task = send_response.root.result

#         # # Extract and log the response from the task
#         # print(f"✅ Received response from {agent_name}")

#         # # Extract artifacts (the actual response content) for logging
#         # if hasattr(task, 'artifacts') and task.artifacts:
#         #     print(f"📦 Found {len(task.artifacts)} artifacts in response")
#         #     response_text = ""
#         #     for artifact in task.artifacts:
#         #         if hasattr(artifact, 'parts'):
#         #             for part in artifact.parts:
#         #                 if hasattr(part, 'text') and part.text:
#         #                     response_text += part.text

#         #     if response_text:
#         #         print(f"📝 Response length: {len(response_text)} characters")
#         #         print(f"📄 Response preview: {response_text[:200]}...")
#         #     else:
#         #         print("⚠️ No text content found in artifacts")
#         # else:
#         #     print("⚠️ No artifacts found in task response")

#         # Return the task object as expected by the Gradio interface
#         return task


# def _get_initialized_routing_agent_sync() -> Agent:
#     """Synchronously creates and initializes the RoutingAgent."""

#     async def _async_main() -> Agent:
#         routing_agent_instance = await RoutingAgent.create(
#             remote_agent_addresses=[
#                 os.getenv('AIR_AGENT_URL', 'http://localhost:10002'),
#                 os.getenv('WEA_AGENT_URL', 'http://localhost:10001'),
#                 os.getenv('TRIP_AGENT_URL', 'http://localhost:10003'),
#                 os.getenv('EVENT_AGENT_URL', 'http://localhost:10004'),
#                 os.getenv('FINANCE_AGENT_URL', 'http://localhost:10005'),
#                 os.getenv('FLIGHT_AGENT_URL', 'http://localhost:10006'),
#                 os.getenv('HOTEL_AGENT_URL', 'http://localhost:10007'),
#             ]
#         )
#         return routing_agent_instance.create_agent()

#     try:
#         return asyncio.run(_async_main())
#     except RuntimeError as e:
#         if 'asyncio.run() cannot be called from a running event loop' in str(e):
#             print(
#                 f'Warning: Could not initialize RoutingAgent with asyncio.run(): {e}. '
#                 'This can happen if an event loop is already running (e.g., in Jupyter). '
#                 'Consider initializing RoutingAgent within an async function in your application.'
#             )
#         raise


# root_agent = _get_initialized_routing_agent_sync()
