# pylint: disable=logging-fstring-interpolation
"""
Sub Agent Searcher
负责接收 planner 的计划，分解任务，并从注册中心查找合适的 sub agents
"""
import os
import sys
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PARENT_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, PARENT_DIR)

from routing_agent import RoutingAgent as RegistryRoutingAgent


class SubAgentSearcher:
    """
    Sub Agent Searcher Agent
    职责：
    1. 接收 planner 生成的计划
    2. 将计划分解为多个子任务
    3. 为每个子任务从注册中心查找合适的 sub agent
    4. 将结果保存到 context.state 供后续 agent 使用
    """
    
    def __init__(self):
        self.registry_base_url = os.getenv("REGISTRY_BASE_URL")
        if not self.registry_base_url:
            raise ValueError("REGISTRY_BASE_URL environment variable not set")
    
    def create_agent(self) -> LlmAgent:
        """Create the Sub Agent Searcher LlmAgent."""
        return LlmAgent(
            model='gemini-2.5-flash',
            name='SubAgentSearcher',
            instruction=self.root_instruction,
            description='Analyzes plan and searches for appropriate sub-agents from registry',
            tools=[self.search_agents],
            output_key="agent_search_results"
        )
    
    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate instruction for the agent."""
        plan = context.state.get('plan', 'No plan available.')
        
        return f"""You are a Sub-Agent Discovery Specialist. Your role is to analyze task plans and identify which specialized agents are needed.

**LANGUAGE INSTRUCTION:**
- ALWAYS respond in the SAME language as the plan
- If the plan is in Chinese (中文), respond in Chinese
- If the plan is in English, respond in English

**Plan from Planner:**
{plan}

**Your Responsibilities:**
1. **Analyze** the plan and identify distinct sub-tasks
2. **Extract keywords** for each sub-task to search for appropriate agents
3. **Call search_agents** tool for each identified sub-task with appropriate keyword
4. **Aggregate** all search results

**Available Keywords for Agent Search:**
- `"weather"` → for weather forecasts, climate, temperature
- `"accommodations"` → for hotels, rooms, stays, booking
- `"tripadvisor"` → for attractions, restaurants, reviews
- `"location"` → for places, addresses, geographic search
- `"transport"` → for flights, trains, buses, transportation

**Instructions:**
- For each sub-task in the plan, determine the most appropriate keyword
- Call `search_agents(keyword, task_description, topk)` for each sub-task
- topk=3 means get top 3 matching agents
- The tool will return agent information (name, url, agent_card)
- After all searches complete, provide a summary of found agents

**Example:**
If plan has:
1. Check weather for Los Angeles
2. Find hotels in Los Angeles
3. Search attractions

You should call:
- search_agents(keyword="weather", task="Check weather for Los Angeles", topk=3)
- search_agents(keyword="accommodations", task="Find hotels in Los Angeles", topk=3)
- search_agents(keyword="tripadvisor", task="Search attractions", topk=3)

Start by analyzing the plan and making the necessary search_agents calls."""
    
    async def search_agents(
        self, 
        keyword: str, 
        task: str, 
        topk: int,
        tool_context: ToolContext
    ) -> dict[str, Any]:
        """
        Search for appropriate agents from registry based on keyword and task.
        
        Args:
            keyword: Search keyword (weather, accommodations, tripadvisor, location, transport)
            task: Task description to help registry find best match
            topk: Number of top matching agents to return
            tool_context: ADK tool context for state management
            
        Returns:
            Structured agent information including names, URLs, and agent cards
        """
        # Skip LLM summarization - return API results directly
        tool_context.actions.skip_summarization = True
        
        # Query registry
        router = RegistryRoutingAgent(self.registry_base_url)
        topk_list, agent_list = await router.resolve_client(keyword, task, topk)
        
        # Extract structured information
        agent_infos = []
        for name, url in topk_list:
            agent_infos.append({
                "name": name,
                "url": url,
                "keyword": keyword,
                "task": task
            })
        
        # Save to state for next agent to use
        state = tool_context.state
        if "discovered_agents" not in state:
            state["discovered_agents"] = []
        
        # Append new discoveries
        state["discovered_agents"].extend(agent_infos)
        
        # Also save raw registry response
        if "registry_responses" not in state:
            state["registry_responses"] = {}
        
        state["registry_responses"][keyword] = {
            "topk_list": topk_list,
            "agent_list": agent_list,
            "task": task
        }
        
        return {
            "keyword": keyword,
            "task": task,
            "found_agents": agent_infos,
            "total_candidates": len(agent_list),
            "message": f"Found {len(agent_infos)} agents for keyword '{keyword}'"
        }


def create_sub_agent_searcher() -> LlmAgent:
    """Factory function to create SubAgentSearcher agent."""
    searcher = SubAgentSearcher()
    return searcher.create_agent()
