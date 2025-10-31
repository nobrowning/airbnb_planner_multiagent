import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


def create_airbnb_agent() -> LlmAgent:
    """Constructs the Airbnb ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='airbnb_agent',
        description='An agent that can help with searching accommodation',
        instruction="""You are a specialized assistant for Airbnb accommodations. Your primary function is to utilize the provided tools to search for Airbnb listings and answer related questions. You must rely exclusively on these tools for information; do not invent listings or prices. Ensure that your Markdown-formatted response includes all relevant tool output, with particular emphasis on providing direct links to listings""",
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command='npx',
                    args=['-y', '@openbnb/mcp-server-airbnb', '--ignore-robots-txt'],
                ),
            )
        ],
    )
