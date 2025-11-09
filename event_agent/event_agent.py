import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters


def create_event_agent() -> LlmAgent:
    """Constructs the Event ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    # Get the absolute path to the MCP server script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_python = 'python'  # Use system Python
    mcp_server_script = os.path.join(base_dir, 'event_server', 'main.py')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='event_agent',
        description='An agent that can help search for events, festivals, concerts, and other activities using Google Events',
        instruction="""You are a specialized Event assistant. Your primary function is to utilize the provided tools to search for events, concerts, festivals, art shows, networking events, and other activities. You must rely exclusively on these tools for data and refrain from inventing information.

Key responsibilities:
- Search for events based on location, date, and event type
- Filter and analyze events by various criteria (date, type, venue)
- Provide detailed event information including venue, tickets, and timing
- Help users discover interesting events based on their interests
- Compare and recommend events based on user preferences

Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. When providing event information, include titles, dates, venues, ticket information, and other relevant details.""",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=mcp_python,
                        args=[mcp_server_script],
                    ),
                ),
            )
        ],
    )
