import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters


def create_finance_agent() -> LlmAgent:
    """Constructs the Finance ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')

    # Get the absolute path to the MCP server script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_python = 'python'  # Use system Python
    mcp_server_script = os.path.join(base_dir, 'finance_server', 'main.py')

    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='finance_agent',
        description='An agent that can help with stock market information, currency conversion, and financial data using Google Finance',
        instruction="""You are a specialized Finance assistant. Your primary function is to utilize the provided tools to search for stock information, convert currencies, analyze market data, and provide financial insights. You must rely exclusively on these tools for data and refrain from inventing information.

Key responsibilities:
- Look up stock prices and company information
- Convert currencies with real-time exchange rates
- Provide market overviews and trends
- Analyze historical stock data
- Filter and compare financial instruments
- Offer insights on price movements and market conditions

Ensure that all responses include the detailed output from the tools used and are formatted in Markdown. When providing financial information, include current prices, exchange rates, market trends, and relevant statistics. Always include disclaimers that this is not financial advice.""",
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
