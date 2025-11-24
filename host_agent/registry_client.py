import os
import httpx
from registry_models import RegistryListReq, RegistryListResp


class RegistryClient:
    """子系统2 -> Registry 的 HTTP 客户端：我们写请求体，解析响应体。"""

    def __init__(self, base_url: str, timeout: float = 8.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # 从环境变量读取 API KEY（如果没设置就用默认 dev-admin-api-key）
        self.api_key = os.getenv("API_KEY", "dev-admin-api-key")

        # 每次请求都要带 Authorization 头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def list_agents(self, keyword: str, req: RegistryListReq) -> RegistryListResp:
        """
        调用 API 1：POST /api/v1/{keyword}/list
        """
        url = f"{self.base_url}/api/v1/{keyword}/list"

        async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as cli:
            r = await cli.post(url, json=req, headers=self.headers)

            # 401/403 等会在这里抛出
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError:
                print("\n❌ Registry returned error:", r.text)
                print("Request JSON:", req.model_dump())
                raise


            return RegistryListResp.model_validate(r.json())
