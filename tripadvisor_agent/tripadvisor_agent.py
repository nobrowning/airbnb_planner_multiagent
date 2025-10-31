import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


def create_tripadvisor_agent() -> LlmAgent:
    """Constructs the TripAdvisor ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    # Get the absolute path to the MCP server's Python interpreter
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mcp_python = os.path.join(base_dir, '.venv', 'Scripts', 'python.exe')
    mcp_server_script = os.path.join(base_dir, 'server.py')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='tripadvisor_agent',
        description='An agent that can help with TripAdvisor searches for attractions, restaurants, and reviews',
        instruction="""You are a specialized TripAdvisor assistant. Your primary function is to utilize the provided tools to search for locations, attractions, restaurants, and reviews on TripAdvisor. You must rely exclusively on these tools for data and refrain from inventing information. Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. When providing location information, include ratings, addresses, and other relevant details.""",
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command=mcp_python,
                    args=[mcp_server_script],
                ),
            )
        ],
    )
