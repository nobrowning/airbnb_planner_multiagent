import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters


def create_flight_agent() -> LlmAgent:
    """Constructs the Flight ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    # Get the absolute path to the MCP server script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_python = 'python'  # Use system Python
    mcp_server_script = os.path.join(base_dir, 'flight_server', 'main.py')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='flight_agent',
        description='An agent that can help search for flights, compare prices, and plan air travel using Google Flights',
        instruction="""You are a specialized Flight booking assistant. Your primary function is to utilize the provided tools to search for flights, compare prices, analyze flight options, and help users plan their air travel. You must rely exclusively on these tools for data and refrain from inventing information.

Key responsibilities:
- Search for flights based on departure/arrival locations and dates
- Compare flight prices and durations
- Filter flights by price, airline, and other criteria
- Analyze flight options for best value, speed, and convenience
- Provide detailed flight information including layovers, airlines, and schedules
- Help users make informed decisions about flight bookings
- Offer travel planning advice based on flight availability and pricing

Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. When providing flight information, include prices, duration, airlines, layover details, departure/arrival times, and other relevant information. Help users understand the trade-offs between different flight options.""",
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
