# pylint: disable=logging-fstring-interpolation
"""
Sub Agent Caller
负责接收搜索到的 sub agent 信息，建立连接，并调用这些 agents 完成任务
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable

import httpx
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)

from remote_agent_connection import RemoteAgentConnections


class SubAgentCaller:
    """
    Sub Agent Caller Agent
    职责：
    1. 在 before_model_callback 中读取 discovered_agents
    2. 建立与这些 agents 的连接
    3. 提供 send_message 工具调用 sub agents
    4. 收集和返回结果
    """
    
    def __init__(self):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.agent_cards: dict[str, AgentCard] = {}
        self.available_agents_info: list[dict] = []
    
    def create_agent(self) -> LlmAgent:
        """Create the Sub Agent Caller LlmAgent."""
        return LlmAgent(
            model='gemini-2.5-flash',
            name='SubAgentCaller',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description='Calls remote sub-agents to execute tasks based on discovered agents',
            tools=[self.send_message],
            output_key="results"
        )
    
    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate dynamic instruction based on available agents."""
        plan = context.state.get('plan', 'No plan available.')
        agent_search_results = context.state.get('agent_search_results', 'No search results.')
        
        # Build agent roster from available agents
        agent_roster = []
        for agent_info in self.available_agents_info:
            agent_roster.append(f"- **{agent_info['name']}** ({agent_info['url']}) - Keyword: {agent_info['keyword']}")
        
        agent_roster_text = "\n".join(agent_roster) if agent_roster else "No agents available."
        
        return f"""You are a Sub-Agent Orchestrator. Your role is to delegate tasks to specialized remote agents and coordinate their work.

**LANGUAGE INSTRUCTION:**
- ALWAYS respond in the SAME language as the plan
- If the plan is in Chinese (中文), respond in Chinese
- If the plan is in English, respond in English

**IMPORTANT CONTEXT:**
- Today's date is: {datetime.now().strftime("%A, %B %d, %Y")}
- Use this date to interpret relative time expressions

**Original Plan:**
{plan}

**Agent Search Results:**
{agent_search_results}

**Available Sub-Agents:**
{agent_roster_text}

**Your Responsibilities:**
1. **Execute** the plan by delegating sub-tasks to appropriate agents
2. **Use send_message** tool to communicate with each sub-agent
3. **Provide context** - enrich task descriptions with all necessary information
4. **Coordinate** multiple agents if needed (call them in appropriate order or in parallel)
5. **Collect results** from all agents
6. **Handle errors** gracefully if an agent fails

**Core Directives:**
- Use `send_message(agent_name, task)` to delegate work
- `agent_name` must match one of the available agent names listed above
- `task` should be clear, specific, and include all context the agent needs
- Always include specific dates when relevant (based on today's date)
- Call multiple agents if the plan requires it
- Present complete responses from agents

**Example:**
If you have Weather Agent and Airbnb Agent available, and plan says:
1. Check weather for Los Angeles this weekend
2. Find hotels for that weekend

You should:
1. send_message(agent_name="Weather Agent", task="What's the weather forecast for Los Angeles on Saturday January 25 and Sunday January 26, 2025?")
2. send_message(agent_name="Airbnb Agent", task="Find available accommodations in Los Angeles for January 25-26, 2025")

Start executing the plan by calling appropriate agents."""
    
    async def before_model_callback(
        self, 
        callback_context: CallbackContext, 
        llm_request
    ) -> None:
        """
        Before model callback - initialize connections to discovered agents.
        This runs before the LLM generates its response.
        """
        state = callback_context.state
        
        # Get discovered agents from state
        discovered_agents = state.get("discovered_agents", [])
        
        if not discovered_agents:
            print("[SubAgentCaller] No discovered agents in state")
            return
        
        print(f"[SubAgentCaller] Initializing connections to {len(discovered_agents)} agents...")
        
        # Initialize connections for each discovered agent
        for agent_info in discovered_agents:
            agent_name = agent_info["name"]
            agent_url = agent_info["url"]
            
            # Skip if already connected
            if agent_name in self.remote_agent_connections:
                continue
            
            try:
                await self._connect_to_agent(agent_name, agent_url)
                self.available_agents_info.append(agent_info)
                print(f"[SubAgentCaller] ✅ Connected to {agent_name}")
            except Exception as e:
                print(f"[SubAgentCaller] ❌ Failed to connect to {agent_name}: {e}")
        
        print(f"[SubAgentCaller] Total connected agents: {len(self.remote_agent_connections)}")
    
    async def _connect_to_agent(self, agent_name: str, agent_url: str) -> None:
        """
        Establish connection to a remote agent by fetching its agent card.
        
        Args:
            agent_name: Name of the agent
            agent_url: URL of the agent
        """
        if not agent_url or not isinstance(agent_url, str) or not agent_url.startswith("http"):
            raise ValueError(f"Invalid URL for {agent_name}: {agent_url}")
        
        # Fetch agent card
        async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
            url = agent_url.rstrip("/")
            response = await client.get(f"{url}/.well-known/agent-card.json")
            response.raise_for_status()
            
            agent_card_data = response.json()
            agent_card = AgentCard.model_validate(agent_card_data)
        
        # Create connection
        remote_connection = RemoteAgentConnections(
            agent_card=agent_card,
            agent_url=agent_url
        )
        
        self.remote_agent_connections[agent_name] = remote_connection
        self.agent_cards[agent_name] = agent_card
    
    async def send_message(
        self, 
        agent_name: str, 
        task: str, 
        tool_context: ToolContext
    ) -> dict[str, Any]:
        """
        Send a task to a specific sub-agent.
        
        Args:
            agent_name: Name of the target agent (must be one of the discovered agents)
            task: Task description to send to the agent
            tool_context: ADK tool context
            
        Returns:
            Response from the sub-agent
        """
        # Check if agent is connected
        if agent_name not in self.remote_agent_connections:
            return {
                "error": f"Agent '{agent_name}' not found or not connected",
                "available_agents": list(self.remote_agent_connections.keys())
            }
        
        client = self.remote_agent_connections[agent_name]
        state = tool_context.state
        
        # Prepare message
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())
        
        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                "contextId": context_id,
            }
        }
        
        message_request = SendMessageRequest(
            id=message_id,
            params=MessageSendParams.model_validate(payload),
        )
        
        try:
            # Send message to agent
            send_response = await client.send_message(message_request)
            
            # Extract text from response
            response_text = self._extract_response_text(send_response)
            
            return {
                "agent": agent_name,
                "task": task,
                "response": response_text,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "agent": agent_name,
                "task": task,
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_response_text(self, response: Any) -> str:
        """Extract text from various response types."""
        # Task type
        if isinstance(response, Task):
            if response.artifacts and response.artifacts[0].parts:
                return response.artifacts[0].parts[0].root.text
            if response.history:
                agent_msgs = [m for m in response.history if getattr(m, "role", None) == "agent"]
                if agent_msgs and agent_msgs[-1].parts:
                    return agent_msgs[-1].parts[0].root.text
        
        # SendMessageResponse type
        elif isinstance(response, SendMessageResponse):
            root = getattr(response, "root", None)
            if isinstance(root, SendMessageSuccessResponse):
                if isinstance(root.result, Task):
                    return self._extract_response_text(root.result)
        
        # Fallback
        return str(response)


def create_sub_agent_caller() -> LlmAgent:
    """Factory function to create SubAgentCaller agent."""
    caller = SubAgentCaller()
    return caller.create_agent()
