import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters


def create_hotel_agent() -> LlmAgent:
    """Constructs the Hotel ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    # Get the absolute path to the MCP server script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_python = 'python'  # Use system Python
    mcp_server_script = os.path.join(base_dir, 'hotel_server', 'main.py')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='hotel_agent',
        description='An agent that can help search for hotels, vacation rentals, and accommodations using Google Hotels',
        instruction="""You are a specialized Hotel and Accommodation assistant. Your primary function is to utilize the provided tools to search for hotels, vacation rentals, and other accommodations, compare prices, analyze amenities, and help users plan their stays. You must rely exclusively on these tools for data and refrain from inventing information.

Key responsibilities:
- Search for hotels and vacation rentals based on location and dates
- Compare hotel prices, ratings, and amenities
- Filter accommodations by price, rating, class, amenities, and property type
- Get detailed property information including rooms, facilities, and policies
- Analyze accommodation options for best value, location, and quality
- Provide personalized recommendations based on user preferences
- Help users make informed decisions about bookings
- Offer accommodation planning advice and neighborhood insights

Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. When providing hotel information, include prices, ratings, amenities, location details, guest reviews, and cancellation policies. Help users understand the trade-offs between different accommodation options and provide context about neighborhoods and accessibility.""",
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
