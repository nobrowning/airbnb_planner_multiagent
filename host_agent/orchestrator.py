import asyncio
import os
from datetime import datetime
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from host_router import root_agent as routing_agent


class OrchestratorAgent:
    """Orchestrator agent that coordinates multiple LlmAgents in sequence."""
    
    def __init__(self):
        self.planner = None
        self.router = None  # 使用 routing_agent 作为路由器
        self.summarizer = None
        self.orchestrator = None
    
    async def _async_init_components(self) -> None:
        """Asynchronously initialize all LlmAgent components."""
        print("Initializing Orchestrator components...")
        
        # Create planner agent
        self.planner = LlmAgent(
            name="PlanActions",
            instruction=lambda c: f"""You are a Task Decomposition Planner. Your role is to analyze complex user requests and break them down into clear, actionable sub-tasks.

**LANGUAGE INSTRUCTION:**
- ALWAYS respond in the SAME language as the user's input
- If the user writes in Chinese (中文), respond in Chinese
- If the user writes in English, respond in English
- Detect the language from the user's query and match it exactly

**IMPORTANT CONTEXT:
- Today's date is: {datetime.now().strftime("%A, %B %d, %Y")}
- Use this date to interpret relative time expressions like "this weekend", "next week", "tomorrow", etc.
- When planning tasks involving dates, always provide specific dates based on today's date

**Your Responsibilities:**
1. **Analyze** the user's request to understand their complete needs
2. **Identify** all required information: weather, accommodations, flights, hotels, events, attractions, restaurants, or financial data
3. **Decompose** the complex request into multiple independent sub-tasks
4. **Prioritize** sub-tasks in logical order (e.g., check weather before planning activities)
5. **Specify** what information each sub-task should gather
6. **Define** dependencies between sub-tasks if any exist
7. **Include specific dates** in your plan when the user mentions relative time periods

**Output Format:**
Provide a structured plan with:
- List of sub-tasks (numbered)
- For each sub-task: clear objective, required agent type, expected output
- Dependencies between tasks if applicable
- Overall goal of the plan
- Specific dates when applicable

**Example:**
User: "Plan a weekend trip to Los Angeles"
Your output:
1. Check weather forecast for Los Angeles this weekend (Saturday, January 25 and Sunday, January 26)
2. Find available accommodations in Los Angeles for January 25-26
3. Search for local events and attractions during that weekend
4. Get restaurant recommendations
5. Estimate total trip cost

Do NOT execute tasks - only create the plan. The routing agent will handle execution.""",
            output_key="plan",
            model="gemini-2.5-flash",
            # planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(include_thoughts=True))
        )
        
        # Use the already initialized routing agent from routing_agent.py
        print("Using pre-initialized Routing Agent...")
        self.router = routing_agent
        print("Routing Agent loaded successfully.")
        
        # Create summarizer agent
        self.summarizer = LlmAgent(
            name="ResultSummarizer",
            instruction=lambda c: f"""You are a Result Synthesis and Presentation Agent. Your role is to transform raw data from multiple agents into a comprehensive, user-friendly final report.

**LANGUAGE INSTRUCTION:**
- ALWAYS respond in the SAME language as the original user input
- If the user wrote in Chinese (中文), respond in Chinese
- If the user wrote in English, respond in English
- Match the language used in the user's original query

**IMPORTANT CONTEXT:
- Today's date is: {datetime.now().strftime("%A, %B %d, %Y")}
- Use this date context when interpreting and presenting temporal information in the results

**Raw Results from Agents:**
{c.state.get('results', 'No results available.')}

**Your Responsibilities:**
1. **Synthesize** information from all sub-tasks executed by the routing agent
2. **Identify** connections and patterns across different data sources
3. **Highlight** key insights, important details, and actionable recommendations
4. **Organize** information in a logical, easy-to-follow structure
5. **Enrich** the response with context and explanations where helpful
6. **Present** data in a visually appealing format (use markdown formatting)
7. **Add** practical suggestions based on the gathered information

**Output Format:**
- **Executive Summary**: Brief overview of findings
- **Detailed Sections**: Organized by topic (weather, accommodations, activities, etc.)
  - Use bullet points, numbered lists, and tables where appropriate
  - Highlight prices, dates, and important warnings
- **Key Insights**: Connect information across different agents
- **Recommendations**: Practical next steps for the user
- **Summary**: Final thoughts and suggestions

**Formatting Guidelines:**
- Use **bold** for important information
- Use bullet points for lists
- Include relevant emojis for better readability (🌤️ ☀️ 🏨 🍽️ 💰)
- Use tables for comparing options
- Add section headers with ###

Your goal is to provide a polished, professional, and actionable final report that exceeds user expectations.""",
            model="gemini-2.5-flash",
            # planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(include_thoughts=True))
        )
        
        # Create the sequential orchestrator
        self.orchestrator = SequentialAgent(
            name="Orchestrator",
            sub_agents=[self.planner, self.router, self.summarizer]
        )
        
        print("Orchestrator components initialized successfully.")
    
    @classmethod
    async def create(cls) -> 'OrchestratorAgent':
        """Create and asynchronously initialize an instance of OrchestratorAgent."""
        instance = cls()
        await instance._async_init_components()
        return instance
    
    def get_agent(self) -> SequentialAgent:
        """Get the orchestrator agent instance."""
        return self.orchestrator


def _get_initialized_orchestrator_sync() -> SequentialAgent:
    """Synchronously creates and initializes the Orchestrator."""
    
    async def _async_main() -> SequentialAgent:
        orchestrator_instance = await OrchestratorAgent.create()
        return orchestrator_instance.get_agent()
    
    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            print(
                f'Warning: Could not initialize Orchestrator with asyncio.run(): {e}. '
                'This can happen if an event loop is already running (e.g., in Jupyter). '
                'Consider initializing Orchestrator within an async function in your application.'
            )
        raise


# Initialize the orchestrator using the async pattern
orchestrator = _get_initialized_orchestrator_sync()
