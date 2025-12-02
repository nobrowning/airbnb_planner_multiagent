# pylint: disable=logging-fstring-interpolation
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Callable

from google.genai import types
from google.adk.runners import Runner
import httpx
from types import SimpleNamespace

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
    Message,
    TextPart,
)

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

from remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)
load_dotenv()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # /home/bupt/agent/A2A/host_agent
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)                   # /home/bupt/agent/A2A
PARENT_DIR = os.path.dirname(PROJECT_ROOT)                    # /home/bupt/agent
sys.path.insert(0, PARENT_DIR)
from routing_agent import RoutingAgent as RegistryRoutingAgent
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
class HostRoutingAgent:
    """The Routing agent.

    This is the agent responsible for choosing which remote seller agents to send
    tasks to and coordinate their work.
    """

    def __init__(
        self,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''
        self.debug_callback: Callable[[str], None] | None = None
        self.debug_runtime_buffer: list[str] = []

    async def _async_init_components(
        self,
        remote_agent_addresses: list[str],
        agent_names: list[str],
    ) -> None:
        """Initialize connections to remote agents with actual connectivity check."""

        import httpx

        for agent_name, address in zip(agent_names, remote_agent_addresses):

            # 已存在则跳过
            if agent_name in self.remote_agent_connections:
                continue

            # URL 无效（None、空字符串、不是 http）
            if not address or not isinstance(address, str) or not address.startswith("http"):
                raise ValueError(f"Invalid URL for {agent_name}: {address}")
                continue

            try:
                # 🔥 尝试真实访问 /card（A2A agent 标准健康检查接口）
                async with httpx.AsyncClient(timeout=3.0, verify=False) as client:
                    address_ = address[:-1] if address.endswith("/") else address
                    response = await client.get(f"{address_}/.well-known/agent-card.json")
                    response.raise_for_status()  # 如果状态码不是 2xx,抛出异常
                    
                    # 解析并保存 agent card 信息
                    agent_card_data = response.json()
                    agent_card = AgentCard.model_validate(agent_card_data)

                # 🔥 真正可达：创建连接
                remote_connection = RemoteAgentConnections(
                    agent_card=agent_card,
                    agent_url=address
                )
                self.remote_agent_connections[agent_name] = remote_connection
                self.cards[agent_name] = agent_card  # 保存 card 信息到字典

                print(f"[RoutingAgent] 🔗 Connected to {agent_name} @ {address}")

            except Exception as e:
                raise RuntimeError(f"Failed to connect to {agent_name} @ {address}: {e}")

        # 记录连接信息（仅作调试用途）
        self.agents = "\n".join(
            [f"{{'name': '{name}', 'url': '{url}'}}" for name, url in zip(agent_names, remote_agent_addresses)]
        )
    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
        task_callback: TaskUpdateCallback | None = None,
    ) -> 'HostRoutingAgent':
        """Create and asynchronously initialize an instance of the RoutingAgent."""
        instance = cls(task_callback)
        instance.remote_agent_connections = {}
        instance.cards = {}
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the RoutingAgent."""
        return LlmAgent(
            model='gemini-2.5-flash',
            name='Routing_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This Routing agent orchestrates the decomposition of the user asking for weather forecast, airbnb accommodation, or tripadvisor searches'
            ),
            tools=[
                self.send_message,
            ],
            output_key="results"
        )
    def _debug(self, text: str):
        """将 send_message 内部的日志缓存起来，最终再统一推送到界面"""
        self.debug_runtime_buffer.append(text)
    
    
    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the RoutingAgent."""
        current_agent = self.check_active_agent(context)
        plan = context.state.get('plan', 'No plan available.')
        
        return f"""
        **IMPORTANT CONTEXT:**
        - Today's date is: {datetime.now().strftime("%A, %B %d, %Y")}
        - Use this date to interpret relative time expressions like "this weekend", "next week", "tomorrow", etc.
        - When delegating tasks involving dates, always provide specific dates based on today's date

        **Role:** You are an expert Routing Delegator. Your primary function is to accurately delegate user inquiries based on the provided plan to the appropriate specialized remote agents.

        **Plan to Execute:**
        {plan}

        **Core Directives:**

        * **Task Delegation:** Utilize the `send_message` function to assign actionable tasks to remote agents.
        * **Contextual Awareness for Remote Agents:** If a remote agent repeatedly requests user confirmation, assume it lacks access to the         full conversation history. In such cases, enrich the task description with all necessary contextual information relevant to that         specific agent.
        * **Autonomous Agent Engagement:** Never seek user permission before engaging with remote agents. If multiple agents are required to         fulfill a request, connect with them directly without requesting user preference or confirmation.
        * **Transparent Communication:** Always present the complete and detailed response from the remote agent to the user.
        * **User Confirmation Relay:** If a remote agent asks for confirmation, and the user has not already provided it, relay this         confirmation request to the user.
        * **Focused Information Sharing:** Provide remote agents with only relevant contextual information. Avoid extraneous details.
        * **No Redundant Confirmations:** Do not ask remote agents for confirmation of information or actions.
        * **Tool Reliance:** Strictly rely on available tools to address user requests. Do not generate responses based on assumptions. If         information is insufficient, request clarification from the user.
        * **Prioritize Recent Interaction:** Focus primarily on the most recent parts of the conversation when processing requests.
        * **Active Agent Prioritization:** If an active agent is already engaged, route subsequent related requests to that agent using the         appropriate task update tool.
        * **Keyword Selection:** 
          Instead of specifying an agent name, you MUST include a `keyword` argument in your function call.
          The keyword MUST be selected from the following list:  
          - `"weather"` → for any question related to climate, temperature, or forecasts  
          - `"accommodations"` → for accommodation, rooms, stays, or booking requests  
          - `"tripadvisor"` → for reviews, sightseeing, attractions, or travel planning
          - `"location"` → for searching places, geographic locations, addresses, nearby POIs, or area-specific information
          - `"transport"` → for transportation options such as flights, trains, buses, driving routes, taxi/hailing services, and mobility planning
        **Agent Roster:**

        **Keyword Set:** ["weather","accommodations","tripadvisor","location","transport"]
        * Currently Active Seller Agent: `{current_agent['active_agent']}`
        **Child Agent:**
            When child agents return results:
            - NEVER mention their names.
            - NEVER output sentences like "Airbnb Agent said", "Weather Agent responded", etc.
            - ALWAYS merge the results into a single coherent natural language answer.
            - The final response MUST NOT explicitly list or quote sub agent responses.
            Your job is to give a clean final answer to the user.
                """
    

    def check_active_agent(self, context: ReadonlyContext):
        state = context.state
        if (
            'session_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'active_agent' in state
        ):
            return {'active_agent': f'{state["active_agent"]}'}
        return {'active_agent': 'None'}

    def before_model_callback(
        self, callback_context: CallbackContext, llm_request
    ):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True

    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.cards:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            print(f'Found agent card: {card.model_dump(exclude_none=True)}')
            print('=' * 100)
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info
    
    async def _connect_to_registry_(self, keyword: str, task: str, topk: int):
        router = RegistryRoutingAgent(os.getenv("REGISTRY_BASE_URL"))  # 创建 Registry Agent
        topk_list,agent_list = await router.resolve_client(keyword, task, topk)
        agent_names = [a[0] for a in topk_list] 
        agent_urls = [a[1] for a in topk_list]
        return agent_names, agent_urls, topk_list,agent_list

    
    async def send_message(
        self, keyword: str, task: str, tool_context: ToolContext
    ):
        """
        Send task to dynamically discovered agents using queue-based structured output.
        """

        # -------- 队列初始化（不会串子任务） --------
        agent_list_queue = []      # 注册中心返回列表队列
        connection_queue = []      # 代理连接成功/失败队列
        debug_queue = []           # 调试队列
        agent_responses = {}       # {"Weather Agent": "...", "Airbnb Agent": "..."}

        def debug(msg):
            debug_queue.append(msg)
        state = tool_context.state
        topk = 3
        # -------- 1. 注册中心 --------
        agent_names, agent_urls, topk_list, agent_list_queue = await self._connect_to_registry_(keyword, task, topk)
        # 记录注册中心结果
        state["active_agent"] = agent_names
        state["registry_candidates"] = topk_list

        # -------- 2. 懒连接每个 agent --------
        for name, url in zip(agent_names, agent_urls):
            try:
                await self._async_init_components([url], [name])
                connection_queue.append({
                    "agent": name,
                    "url": url,
                    "status": "success"
                })
                debug(f"🔌 连接成功：{name} ({url})")
            except Exception as e:
                connection_queue.append({
                    "agent": name,
                    "url": url,
                    "status": f"failure: {e}"
                })
                debug(f"❌ 连接失败：{name} ({url})：{e}")

        # -------- 3. 构造消息 Payload --------
        context_id = state.get("context_id", str(uuid.uuid4()))
        input_metadata = state.get("input_message_metadata", {})
        message_id = input_metadata.get("message_id", str(uuid.uuid4()))

        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                "contextId": context_id,
            }
        }

        debug(f"📤 发送消息给子 Agent: {payload}")

        message_request = SendMessageRequest(
            id=message_id,
            params=MessageSendParams.model_validate(payload),
        )

        # -------- 4. 并发查询所有 Agents --------
        async def query_agent(agent_name: str):
            from a2a.types import SendMessageSuccessResponse, Task, SendMessageResponse
            client = self.remote_agent_connections.get(agent_name)

            if not client:
                debug(f"❌ 无法连接 {agent_name}: 未建立 client")
                return agent_name, {"error": "no active client"}

            try:
                send_response = await client.send_message(message_request)

                # Task 类型（A2A 特有）
                if isinstance(send_response, Task):
                    text = self._extract_task_text(send_response)
                    debug(f"🤖 {agent_name} 返回 Task 文本：{text[:80]}")
                    return agent_name, text

                # SendMessageResponse 类型
                elif isinstance(send_response, SendMessageResponse):
                    root = getattr(send_response, "root", None)
                    if isinstance(root, SendMessageSuccessResponse):
                        if isinstance(root.result, Task):
                            text = self._extract_task_text(root.result)
                            return agent_name, text

                    # fallback
                    return agent_name, str(send_response)

                elif isinstance(send_response, dict):
                    return agent_name, send_response

                else:
                    return agent_name, f"[Unknown response type: {type(send_response)}]"

            except Exception as e:
                debug(f"❌ 调用 {agent_name} 失败：{e}")
                error_details = []
                error_details.append(f"\n====== ERROR FROM {agent_name} ======")
                error_details.append(f"[Type] {type(e)}")
                error_details.append(f"[Error] {e}")
                    # 推到 debug 队列
                debug("\n".join(error_details))
                return agent_name, {"error": str(e)}

        # 并发执行
        results = await asyncio.gather(*(query_agent(name) for name in agent_names))

        # -------- 5. 收集所有子 Agent 的答案 --------
        for name, result in results:
            agent_responses[name] = result
            debug(f"📥 已记录 {name} 的回答")

        # -------- 6. 返回结构化数据（ADK 不会破坏这个结构） --------
        return {
            "type": "multi_agent_response",
            "payload": {
                "agent_list_queue": agent_list_queue,
                "connection_queue": connection_queue,
                "agent_responses": agent_responses,
                "debug_queue": debug_queue,
                "keyword": keyword,
                "task": task,
                "final_instructions": (
            '''
            When child agents return results:
            - NEVER mention their names.
            - NEVER output sentences like "Airbnb Agent said", "Weather Agent responded", etc.
            - ALWAYS merge the results into a single coherent natural language answer.
            - The final response MUST NOT explicitly list or quote sub agent responses.
            Your job is to give a clean final answer to the user.
            '''
                )
            },
        }


    def _extract_task_text(self, task_obj):
        """从 A2A Task 中提取文本"""
        text = None
        if task_obj.artifacts:
            if task_obj.artifacts[0].parts:
                text = task_obj.artifacts[0].parts[0].root.text
        if not text and task_obj.history:
            agent_msgs = [m for m in task_obj.history if getattr(m, "role", None) == "agent"]
            if agent_msgs and agent_msgs[-1].parts:
                text = agent_msgs[-1].parts[0].root.text
        return text or "(no text)"
host_agent_instance = None
def _get_initialized_routing_agent_sync():
    global host_agent_instance

    async def _async_main():
        global host_agent_instance
        host_agent_instance = await HostRoutingAgent.create([])
        return host_agent_instance.create_agent()

    return asyncio.run(_async_main())
root_agent = _get_initialized_routing_agent_sync()