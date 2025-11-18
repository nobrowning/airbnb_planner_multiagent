import asyncio
import traceback  # Import the traceback module
import sys
import io

from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr
from gradio import ChatMessage

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
    history: list[ChatMessage],
):
    """Get response from host agent."""
    messages_buffer = []  # Buffer to accumulate all messages
    agent_call_id2messages_idx_map = {}  # Map agent_call_id to message index

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
                        agent_name = part.function_call.args.get('agent_name', 'unknown_agent')
                        agent_call_id = part.function_call.id
                        
                        formatted_call = f'```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```'
                        
                        # 创建新消息,显示正在调用的 agent
                        new_message = ChatMessage(
                            content=f'🤔 **Calling {agent_name}**\n{formatted_call}',
                            metadata={"title": f"⏳ {agent_name}", "id": agent_call_id, "status": "pending"}
                        )
                        
                        messages_buffer.append(new_message)
                        agent_call_id2messages_idx_map[agent_call_id] = len(messages_buffer) - 1
                        
                        # 立即 yield 以显示思考过程
                        yield messages_buffer
                        
                    elif part.function_response:
                        agent_call_id = part.function_response.id
                        
                        if agent_call_id in agent_call_id2messages_idx_map:
                            idx = agent_call_id2messages_idx_map[agent_call_id]
                            old_message = messages_buffer[idx]
                            
                            # 提取 agent 名称
                            agent_name = old_message.metadata.get('title', 'Agent').replace('⏳', '').strip()
                            old_message.metadata['title'] = f'✅ {agent_name}'
                            
                            response_content = part.function_response.response
                            if isinstance(response_content, dict) and 'response' in response_content:
                                formatted_response_data = response_content['response']
                            else:
                                formatted_response_data = response_content
                            
                            formatted_response = f'```json\n{pformat(formatted_response_data, indent=2, width=80)}\n```'
                            
                            
                            old_message.content += f'\n\n✅ **Response from {agent_name}**\n{formatted_response}'
                            yield messages_buffer
                            await asyncio.sleep(2)
                            old_message.metadata["status"] = "done"
                            yield messages_buffer

            if event.is_final_response():
                final_response_text = ''
                if event.content and event.content.parts:
                    final_response_text = ''.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = f'Agent escalated: {event.error_message or "No specific message."}'
                if final_response_text:
                    new_message = gr.ChatMessage(
                        role='assistant', content=final_response_text
                    )
                    messages_buffer.append(new_message)
                    # Yield all accumulated messages including the final one
                    yield messages_buffer
                break
    except Exception as e:
        print(f'Error in get_response_from_agent (Type: {type(e)}): {e}')
        traceback.print_exc()  # This will print the full traceback
        error_message = gr.ChatMessage(
            role='assistant',
            content='An error occurred while processing your request. Please check the server logs for details.',
        )
        messages_buffer.append(error_message)
        yield messages_buffer

async def main():
    """Main gradio app."""
    print('Creating ADK session...')
    await SESSION_SERVICE.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print('ADK session created successfully.')

    with gr.Blocks(
        title='A2A DEMO',
        css="""
        #component-0 {
            height: 90vh;
        }
        """
    ) as demo:
        gr.ChatInterface(
            get_response_from_agent,
            title='A2A Host Agent',
            description='This assistant can help you to check weather, find airbnb accommodation, and search TripAdvisor for attractions and restaurants',
            type='messages',

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
