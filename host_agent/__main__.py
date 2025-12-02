import asyncio
import traceback  # Import the traceback module
import sys
import io
from a2a.types import Task
from collections.abc import AsyncIterator
from pprint import pformat
import gradio as gr
from gradio import ChatMessage

from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError

# Fix Windows console encoding issue
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Already wrapped or not needed

# from routing_agent import (
#     root_agent as routing_agent,
# )

from orchestrator import orchestrator as routing_agent


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
    messages_buffer: list[ChatMessage] = []  # Buffer to accumulate all messages
    agent_call_id2messages_idx_map: dict[str, int] = {}  # Map agent_call_id to message index

    try:
        event_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)],
            ),
        )
        processing_message_id = "0"
        processing_message = ChatMessage(
            role="assistant",
            content="",
            metadata={
                "title": "Processing",
                "status": "pending",
                "id": processing_message_id,
            },
        )
        messages_buffer.append(processing_message)

        async for event in event_iterator:
            print("***" * 10)
            print(f"Event received: {event}")
            print("***" * 10)

            # ========= 逐个处理 content.parts =========
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # ---------- 工具调用阶段：FunctionCall ----------
                    if part.function_call:
                        agent_name = part.function_call.args.get("agent_name")
                        author = event.author
                        task = part.function_call.args.get("task")

                        tool_name = part.function_call.name  # 'search_agents' / 'send_message' 等

                        # 第一阶段：SubAgentSearcher.search_agents
                        if tool_name == "search_agents":
                            keyword = part.function_call.args.get("keyword", "")
                            topk = part.function_call.args.get("topk", 0)
                            title_name = (
                                f"Registry"
                            )
                        # 第二阶段及其它：调用子 Agent 执行任务
                        else:
                            title_name = agent_name or f"{author} 调用子 Agent 执行任务"

                        agent_call_id = part.function_call.id

                        call_dict = part.function_call.model_dump(exclude_none=True)

                        # 🔥 删除 keyword 字段
                        if "args" in call_dict and "keyword" in call_dict["args"]:
                            del call_dict["args"]["keyword"]

                        # 再格式化输出
                        formatted_call = (
                            "```python\n"
                            f"{pformat(call_dict, indent=2, width=80)}"
                            "\n```"
                        )

                        # 创建新消息, 显示正在调用的 agent
                        new_message = ChatMessage(
                            content=f"🤔 **Calling {title_name}**\n{formatted_call}",
                            metadata={
                                "title": f"⏳ {title_name}",
                                "id": agent_call_id,
                                "status": "pending",
                                "parent_id": processing_message_id,
                                # 记住这是哪个工具的调用，方便 response 阶段区分
                                "tool_name": tool_name,
                            },
                        )

                        messages_buffer.append(new_message)
                        agent_call_id2messages_idx_map[agent_call_id] = (
                            len(messages_buffer) - 1
                        )

                        # 立即 yield 以显示思考过程
                        yield messages_buffer

                    # ---------- 工具返回阶段：FunctionResponse ----------
                    elif part.function_response:
                        agent_call_id = part.function_response.id

                        if agent_call_id in agent_call_id2messages_idx_map:
                            idx = agent_call_id2messages_idx_map[agent_call_id]
                            old_message = messages_buffer[idx]

                            # 这里的 agent_name 其实是“标题里之前的文字”，先去掉前缀再说
                            raw_title = old_message.metadata.get("title", "Agent")
                            agent_name = raw_title.replace("⏳", "").strip()

                            response_content = part.function_response.response
                            tool_name = part.function_response.name  # search_agents / send_message

                            # ============== 1) search_agents 的返回：渲染匹配卡片 + 修改 title ==============
                            if tool_name == "search_agents" and "found_agents" in response_content:
                                agents = response_content["found_agents"]
                                cards_html = ""

                                for ag in agents:
                                    name = ag.get("name", "Unknown Agent")
                                    url = ag.get("url", "N/A")
                                    desc = ag.get("description", "(无描述)")
                                    score = ag.get("score")
                                    version = ag.get("version")

                                    card = f"""
<div style="
    border:1px solid #ccc;
    padding:12px;
    margin:8px 0;
    border-radius:10px;
    background:#fafafa;
    overflow: hidden;
    text-overflow: ellipsis;">
    <div style="font-size:16px; font-weight:bold;">🤖 {name}</div>
    <div><b>📄 描述：</b>{desc}</div>
    <div><b>🔗 URL：</b><a href="{url}" target="_blank">{url}</a></div>
"""
                                    if score is not None:
                                        card += f"""    <div><b>📊 匹配分数：</b>{score}</div>\n"""
                                    if version is not None:
                                        card += f"""    <div><b>🧩 版本：</b>{version}</div>\n"""

                                    card += "</div>\n"
                                    cards_html += card

                                task_text = response_content.get("task", "")
                                total_candidates = response_content.get(
                                    "total_candidates", len(agents)
                                )
                                matched = len(agents)
                                agent_names_str = "、".join(
                                    [a.get("name", "") for a in agents]
                                ) or "无可用 Agent"

                                summary_title = (
                                    f"为【{task_text}】任务，从140个候选Agent中"
                                    f"匹配到{matched}个：{agent_names_str}"
                                )

                                # ✅ 只在 search_agents 的返回里覆盖 title
                                old_message.metadata["title"] = f"✅ {summary_title}"

                                formatted_response = (
                                    f"### 🔍 找到 {matched} 个可用 Agent\n"
                                    f"<div style=\"display:flex; gap:16px; flex-wrap:wrap; align-items:flex-start;\">\n"
                                    f"{cards_html}"
                                    f"</div>"
                                )

                            elif response_content.get("result"):
                                old_message.metadata["title"] = f"✅ {agent_name}"

                                result_object = response_content["result"]
                                if isinstance(result_object, Task):
                                    text_output = (
                                        result_object.artifacts[0]
                                        .parts[0]
                                        .root.text
                                    )
                                    formatted_response = (
                                        f"```markdown\n{text_output}\n```"
                                    )
                                else:
                                    formatted_response = (
                                        "```json\n"
                                        f"{pformat(response_content['response'], indent=2, width=80)}"
                                        "\n```"
                                    )
                            else:
                                old_message.metadata["title"] = f"✅ {agent_name}"
                                formatted_response = (
                                    "```json\n"
                                    f"{pformat(response_content, indent=2, width=80)}"
                                    "\n```"
                                )

                            # 将内容写入消息
                            old_message.content += (
                                f"\n\n💬 **Response from {agent_name}**\n{formatted_response}"
                            )

                            yield messages_buffer
                            await asyncio.sleep(5)
                            old_message.metadata["status"] = "done"
                            yield messages_buffer
            if event.is_final_response():
                final_response_text = ""
                if event.content and event.content.parts:
                    final_response_text = "".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = (
                        f"Agent escalated: {event.error_message or 'No specific message.'}"
                    )

                if final_response_text:
                    event_author = event.author
                    if event_author != "ResultSummarizer":
                        new_message = ChatMessage(
                            role="assistant",
                            content=final_response_text,
                            metadata={
                                "title": event_author,
                                "id": event.id,
                                "status": "pending",
                                "parent_id": processing_message_id,
                            },
                        )
                        messages_buffer.append(new_message)
                    else:
                        new_message = gr.ChatMessage(
                            role="assistant",
                            content=final_response_text,
                        )
                        for msg in messages_buffer:
                            if msg.metadata and "status" in msg.metadata:
                                msg.metadata["status"] = "done"
                        messages_buffer.append(new_message)

                    # Yield all accumulated messages including the final one
                    yield messages_buffer

    except ClientError as e:
        if e.code == 429 or "RESOURCE_EXHAUSTED" in str(e):
            print(
                f"\n⚠️ API Rate Limit Exceeded (429). Please wait a moment before retrying.\nError details: {e}"
            )
            error_message = ChatMessage(
                role="assistant",
                content="⚠️ **System Busy**: The AI service is currently receiving too many requests (Rate Limit Exceeded). Please wait a minute and try again.",
            )
            messages_buffer.append(error_message)
            yield messages_buffer
        else:
            print(f"GenAI ClientError: {e}")
            traceback.print_exc()
            yield messages_buffer
    except Exception as e:
        print(f"Error in get_response_from_agent (Type: {type(e)}): {e}")
        traceback.print_exc()  # This will print the full traceback
        error_message = gr.ChatMessage(
            role="assistant",
            content="An error occurred while processing your request. Please check the server logs for details.",
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
        title='多智能体DEMO',
        css="""
        #component-0 {
            height: 90vh;
        }
        """
    ) as demo:
        gr.ChatInterface(
            get_response_from_agent,
            title='🚀基于语义路由的多智能体协作系统',
            description='系统通过语义理解用户意图，从智能体仓库中动态发现并组建专业Agent团队，实现多智能体协作完成复杂任务。',
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