# logging_plugin.py
from typing import Callable, Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.events.event import Event

# 全局 logger（由 __main__.py 注册）
_chat_logger: Optional[Callable[[str, str], None]] = None


def register_chat_logger(logger: Callable[[str, str], None]):
    """
    在主程序中调用，把 push_chat 传进来。
    """
    global _chat_logger
    _chat_logger = logger


class FunctionCallLogPlugin(BasePlugin):

    def __init__(self, name: str = "function_call_logger"):
        super().__init__(name=name)

    async def on_event(self, invocation_context, event: Event):
        # 捕获 function_call
        if event.actions and event.actions.function_call:
            fc = event.actions.function_call

            if _chat_logger:
                _chat_logger("system", "=== FUNCTION CALL (from Runner) ===")
                _chat_logger("system", f"name = {fc.name}")
                _chat_logger("system", f"args = {fc.args}")

        # 必须返回 event，否则 Runner 会错误
        return event
