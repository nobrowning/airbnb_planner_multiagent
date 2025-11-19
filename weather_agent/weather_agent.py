import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)


def create_weather_agent() -> LlmAgent:
    """Constructs the ADK agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='weather_agent',
        description='An agent that can help questions about weather',
        instruction="""You are a specialized weather forecast assistant. Your primary function is to utilize the provided tools to retrieve and relay weather information in response to user queries.

**Key Guidelines:**
1.  **Rely on Tools:** You must rely exclusively on the provided tools for data and refrain from inventing information.
2.  **Handling Date Limitations:** If a user requests weather for a date that is too far in the future (e.g., more than 10-14 days ahead) or if the tool cannot return data for the specific requested date:
    *   **Do NOT fail silently or just say "I don't know".**
    *   **Fallback Action:** Instead, query for the **current/upcoming weather forecast** (e.g., next 5-7 days) for that location.
    *   **Inform the User:** Clearly state in your response that the specific date requested is out of range, and you are providing the typical/current weather as a reference.
3.  **Formatting:** Ensure that all responses include the detailed output from the tools used and are formatted in Markdown.""",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='python',
                        args=['./weather_mcp.py'],
                    ),
                    timeout=30.0,
                ),
            )
        ],
    )
