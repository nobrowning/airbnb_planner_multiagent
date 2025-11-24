from typing import Optional

import httpx
from a2a.types import SendMessageRequest, SendMessageResponse


class RemoteAgentConnections:
    """
    直连目标 Agent：
    - 不依赖 AgentCard
    - 直接 POST {base_url}/messages
    - 假设远端 /messages 与 A2A 的请求/响应结构兼容
    """

    def __init__(self, agent_url: str, timeout: float = 30.0) -> None:
        if not agent_url:
            raise ValueError("agent_url is required for direct connection.")
        self.base_url = agent_url.rstrip("/")
        self._httpx = httpx.AsyncClient(timeout=timeout, trust_env=False)

    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        """
        直连 POST {base_url}/messages，并将返回体解析为 A2A 的 SendMessageResponse。
        """
        url = f"{self.base_url}/messages"
        payload = message_request.params.model_dump()  # {'message': {...}}
        resp = await self._httpx.post(url, json=payload)
        resp.raise_for_status()
        return SendMessageResponse.model_validate(resp.json())

    async def aclose(self) -> None:
        await self._httpx.aclose()
