import json
import asyncio
import traceback  # Import the traceback module
import json
import time
import datetime
import os
from a2a.types import Task
from collections.abc import AsyncIterator
from pprint import pformat
import sys
import gradio as gr

from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError
from gradio.chat_interface import ChatMessage
from logging_plugin import FunctionCallLogPlugin, register_chat_logger

chat_history = []
def push_chat(role, text):
    chat_history.append(ChatMessage(role=role, content=text))
    return chat_history
# 注册给插件
register_chat_logger(push_chat)
from orchestrator import orchestrator as routing_agent
from host_router import root_agent ,host_agent_instance
# routing_agent = root_agent
host_router = host_agent_instance       
def host_debug_logger(text: str):
    host_router.debug_runtime_buffer.append(text)

host_router.debug_callback = host_debug_logger
APP_NAME = 'routing_app'
USER_ID = 'default_user'
SESSION_ID = 'default_session'
SESSION_SERVICE = InMemorySessionService()
ROUTING_AGENT_RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
    plugins=[FunctionCallLogPlugin(name="function_call_logger")],
)
from pprint import pformat
import gradio as gr
from typing import AsyncIterator
from google.genai import types
from google.adk.events import Event
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
        processing_message_id = "0"
        processing_message = ChatMessage(
            role='assistant', 
            content="",
            metadata={"title": "Processing", "status": "pending", "id": processing_message_id}
        )
        messages_buffer.append(processing_message)

        async for event in event_iterator:
            print('***'*10)
            print(f'Event received: {event}')
            print('***'*10)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:

                        # 🔥 改成 keyword
                        keyword = part.function_call.args.get('keyword', 'unknown_keyword')
                        agent_call_id = part.function_call.id
                        
                        formatted_call = f'```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```'
                        
                        # 创建新消息,显示正在调用的 task(keyword)
                        new_message = ChatMessage(
                            content=f'🤔 **Calling {keyword}**\n{formatted_call}',
                            metadata={"title": f"⏳ {keyword}", 
                            "id": agent_call_id, "status": "pending",
                            'parent_id': processing_message_id}
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

                            # keyword 替代 agent_name
                            keyword = old_message.metadata.get("title", "task").replace("⏳", "").strip()

                            # 标记完成
                            old_message.metadata["title"] = f"✅ {keyword}"
                            old_message.metadata["status"] = "done"

                            # --- 解析 payload ---
                            response_raw = part.function_response.response
                            if isinstance(response_raw, dict) and response_raw.get("type") == "multi_agent_response":
                                payload = response_raw["payload"]
                            else:
                                try:
                                    payload = json.loads(response_raw)
                                except:
                                    payload = {}

                            agent_list_queue = payload.get("agent_list_queue", [])
                            connection_queue = payload.get("connection_queue", [])
                            agent_responses = payload.get("agent_responses", {})
                            debug_queue = payload.get("debug_queue", [])

                            # =============== 将所有内容追加到旧消息气泡中 ===============

                            block = []
                            block.append(f"\n\n### 🧩 子任务结果 — `{keyword}`\n")

                            # --- 注册中心 ---
                            block.append("#### 📄 注册中心返回的 Agent 列表\n")
                            block.append("```json\n")
                            for lst in agent_list_queue:
                                block.append(json.dumps(lst, ensure_ascii=False, indent=2) + "\n")
                            block.append("```\n")

                            # --- 连接情况 ---
                            block.append("#### 🔌 代理连接情况\n")
                            block.append("```text\n")
                            for conn in connection_queue:
                                block.append(f"{conn['agent']} -> {conn['status']} ({conn['url']})\n")
                            block.append("```\n")

                            # --- Debug 信息 ---
                            if debug_queue:
                                block.append("#### 📋 Debug 信息\n")
                                block.append("```text\n")
                                for dbg in debug_queue:
                                    block.append(dbg + "\n")
                                block.append("```\n")

                            # --- 子 Agent 回复内容 ---
                            block.append("#### 🤖 子 Agent 回复\n")
                            for agent_name, content in agent_responses.items():
                                block.append(f"\n##### {agent_name}\n")
                                if isinstance(content, str):
                                    block.append(content.strip() + "\n")
                                else:
                                    block.append("```json\n")
                                    block.append(json.dumps(content, ensure_ascii=False, indent=2))
                                    block.append("\n```\n")
                            # 追加到原消息内容
                            old_message.content += "".join(block)
                            # 立即刷新 UI
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
                    event_author = event.author
                    if event_author != "ResultSummarizer":
                        new_message = ChatMessage(
                            role='assistant', content=final_response_text,
                            metadata={"title": event_author, "id": event.id,
                                      "status": "pending", 'parent_id': processing_message_id}
                        )
                        messages_buffer.append(new_message)
                    else:
                        new_message = gr.ChatMessage(
                            role='assistant', content=final_response_text
                        )
                        for message in messages_buffer:
                            if message.metadata and "status" in message.metadata:
                                message.metadata["status"] = "done"
                        messages_buffer.append(new_message)
                    # Yield all accumulated messages including the final one
                    yield messages_buffer
                # break
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
