import asyncio
import traceback  # Import the traceback module
import sys
import io

from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr

from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Fix Windows console encoding issue
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Already wrapped or not needed

from routing_agent import (
    root_agent as routing_agent,
)


APP_NAME = 'routing_app'
USER_ID = 'default_user'
SESSION_ID = 'default_session'

SESSION_SERVICE = InMemorySessionService()
ROUTING_AGENT_RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)


async def get_response_from_agent(
    message: str,
    history: list[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """Get response from host agent."""

    # Agent name mapping with emojis
    agent_name_map = {
        'Weather Agent': '🌤️ Weather Agent',
        'Airbnb Agent': '🏠 Airbnb Agent',
        'TripAdvisor Agent': '🗺️ TripAdvisor Agent',
        'Finance Agent': '💰 Finance Agent',
        'Flight Agent': '✈️ Flight Agent',
        'Hotel Agent': '🏨 Hotel Agent',
        'Event Agent': '🎉 Event Agent',
    }

    # Map function_call id to agent name
    function_to_agent = {}
    # Store agent call order and outputs
    agent_sequence = []  # List of (agent_name, output_text, status) tuples
    # status: 'calling' or 'completed'

    def build_accumulated_display():
        """Build accumulated display of all agent statuses and outputs."""
        parts = []
        for agent_name, output_text, status in agent_sequence:
            if status == 'calling':
                parts.append(f'🔄 **正在调用 {agent_name}**')
            elif status == 'completed':
                parts.append(f'**{agent_name}**:\n\n{output_text}')
        return '\n\n---\n\n'.join(parts) if parts else ''

    try:
        event_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(
                role='user', parts=[types.Part(text=message)]
            ),
        )

        async for event in event_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        # Map function call ID to agent name
                        if part.function_call.name == 'send_message' and 'agent_name' in part.function_call.args:
                            agent_name_raw = part.function_call.args.get('agent_name', '')
                            agent_name_formatted = agent_name_map.get(agent_name_raw, agent_name_raw)
                            # Store mapping using function call id
                            if hasattr(part.function_call, 'id'):
                                function_to_agent[part.function_call.id] = agent_name_formatted
                                print(f"\n=== FUNCTION CALL: {agent_name_formatted} with ID {part.function_call.id} ===", flush=True)
                                # Add agent with 'calling' status
                                agent_sequence.append((agent_name_formatted, None, 'calling'))

                                # Yield accumulated display
                                yield gr.ChatMessage(
                                    role='assistant',
                                    content=build_accumulated_display()
                                )
                                print(f"=== YIELDED: Calling {agent_name_formatted} ===", flush=True)
                                await asyncio.sleep(0.3)

                    elif part.function_response:
                        # Get agent name from function response ID
                        agent_name = None
                        if hasattr(part.function_response, 'id'):
                            agent_name = function_to_agent.get(part.function_response.id)

                        # Extract response content
                        response_content = part.function_response.response
                        response_text = ''

                        # Debug: print response structure
                        print(f"\n=== DEBUG: Response for {agent_name} ===")
                        print(f"Response Content Type: {type(response_content)}")

                        # Try to extract from nested 'result' -> 'artifacts' structure
                        print(f"=== STARTING TEXT EXTRACTION for {agent_name} ===")
                        if isinstance(response_content, dict):
                            print("  → response_content is dict")
                            # Check for 'result' key first
                            result_data = response_content.get('result', response_content)
                            print(f"  → result_data type: {type(result_data)}")

                            # Try to get artifacts from the result
                            if hasattr(result_data, 'artifacts'):
                                print("  → result_data has artifacts attribute")
                                # Object with artifacts attribute
                                artifacts = result_data.artifacts
                                for artifact in artifacts:
                                    if hasattr(artifact, 'parts'):
                                        for part_item in artifact.parts:
                                            if hasattr(part_item, 'root') and hasattr(part_item.root, 'text'):
                                                response_text += part_item.root.text + '\n'
                                print(f"  → Extracted {len(response_text)} chars via artifacts attribute")
                            elif isinstance(result_data, dict) and 'artifacts' in result_data:
                                print("  → result_data is dict with 'artifacts' key")
                                # Dict with artifacts key
                                artifacts = result_data['artifacts']
                                if artifacts and len(artifacts) > 0:
                                    for artifact in artifacts:
                                        if isinstance(artifact, dict):
                                            # Try to extract text from parts
                                            if 'parts' in artifact:
                                                parts = artifact['parts']
                                                for part_item in parts:
                                                    if isinstance(part_item, dict) and 'text' in part_item:
                                                        response_text += part_item['text'] + '\n'
                                        elif hasattr(artifact, 'parts'):
                                            for part_item in artifact.parts:
                                                if hasattr(part_item, 'root') and hasattr(part_item.root, 'text'):
                                                    response_text += part_item.root.text + '\n'
                                print(f"  → Extracted {len(response_text)} chars via artifacts dict")
                            else:
                                print(f"  → No artifacts found in result_data")
                        else:
                            print(f"  → response_content is NOT dict")

                        print(f"=== FINISHED TEXT EXTRACTION: {len(response_text)} chars ===", flush=True)

                        # Update agent output in sequence - even if empty or error
                        if agent_name:
                            # Use the extracted text, or a fallback message if extraction failed
                            output_to_store = response_text.strip() if response_text.strip() else "无法获取有效输出"

                            # Find the agent in sequence and update status to 'completed'
                            for i, (name, _, status) in enumerate(agent_sequence):
                                if name == agent_name and status == 'calling':
                                    agent_sequence[i] = (agent_name, output_to_store, 'completed')
                                    print(f"=== STORED OUTPUT for {agent_name} at position {i} ===", flush=True)

                                    # Yield accumulated display with this agent now completed
                                    yield gr.ChatMessage(
                                        role='assistant',
                                        content=build_accumulated_display()
                                    )
                                    print(f"=== YIELDED: Output for {agent_name} ({len(output_to_store)} chars) ===", flush=True)
                                    await asyncio.sleep(0.3)
                                    break

            if event.is_final_response():
                final_response_text = ''
                if event.content and event.content.parts:
                    final_response_text = ''.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = f'Agent escalated: {event.error_message or "No specific message."}'

                # Build final system summary with all agent outputs
                full_output_parts = []
                for agent_name, output_text, status in agent_sequence:
                    if output_text and status == 'completed':  # Only include completed agents
                        full_output_parts.append(f'**{agent_name}**:\n\n{output_text}')
                    elif status == 'calling':
                        print(f"=== WARNING: {agent_name} still in calling state ===", flush=True)
                    else:
                        print(f"=== WARNING: {agent_name} has no output ===", flush=True)

                # Join all agent outputs
                full_output = '\n\n---\n\n'.join(full_output_parts)

                # Add system summary at the beginning
                if full_output:
                    full_output = f'**📊 系统总结**:\n\n{full_output}'

                # Yield the final combined output (this replaces all previous displays)
                if full_output:
                    print(f"=== YIELDING FINAL SYSTEM SUMMARY with {len(agent_sequence)} agents ===", flush=True)
                    yield gr.ChatMessage(
                        role='assistant',
                        content=full_output
                    )
                else:
                    print("=== NO OUTPUT to yield ===", flush=True)
                break

    except Exception as e:
        print(f'Error in get_response_from_agent (Type: {type(e)}): {e}')
        traceback.print_exc()  # This will print the full traceback
        yield gr.ChatMessage(
            role='assistant',
            content='An error occurred while processing your request. Please check the server logs for details.',
        )


async def main():
    """Main gradio app."""
    print('Creating ADK session...')
    await SESSION_SERVICE.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print('ADK session created successfully.')

    with gr.Blocks(
        theme=gr.themes.Ocean(), title='A2A Host Agent with Logo'
    ) as demo:
        gr.Image(
            '../assets/a2a-logo-black.svg',
            width=100,
            height=100,
            scale=0,
            show_label=False,
            show_download_button=False,
            container=False,
            show_fullscreen_button=False,
        )
        gr.ChatInterface(
            get_response_from_agent,
            title='A2A Host Agent',
            description='This assistant can help you by coordinating seven specialized agents — Weather, Airbnb, TripAdvisor, Event, Hotel, Flight, and Finance — through a central Host Agent to provide an integrated experience for travel, discovery, and daily insights.',
        )

    print('Launching Gradio interface...')
    demo.queue().launch(
        server_name='127.0.0.1',
        server_port=8083,
        share=False,
        prevent_thread_lock=False,
    )
    print('Gradio application has been shut down.')


if __name__ == '__main__':
    asyncio.run(main())
