# Hotel Agent

[English](README.md)

## Agent 简介

Hotel Agent 是一个专门用于搜索酒店和住宿的智能体。通过集成 Google Hotels 和 SerpAPI，它提供全面的酒店搜索功能，支持多种筛选条件，帮助用户找到完美的住宿地点。

**主要功能：**
- 搜索酒店、度假村、民宿、公寓等多种住宿类型
- 按价格、评分、设施、星级、房型筛选
- 提供详细信息（房型、设施、政策、评价）
- 比较不同住宿的价格和评分
- 支持免费取消和特殊优惠筛选

**端口：** `10007`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd hotel_agent
   cp example.env .env
   ```

2. **配置 API Key**

   编辑 `.env` 文件，填入以下配置：

   ```env
   # Google Gemini API（必需）
   GOOGLE_API_KEY=your_google_api_key
   LITELLM_MODEL=gemini-2.5-flash

   # Vertex AI（可选）
   GOOGLE_GENAI_USE_VERTEXAI=True
   GOOGLE_CLOUD_PROJECT=your_project_id
   GOOGLE_CLOUD_LOCATION=global
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

   # SerpAPI（必需）
   SERPAPI_KEY=your_serpapi_key_here
   ```

   **获取 API Key：**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - SerpAPI Key: https://serpapi.com/

### 启动命令

```bash
cd hotel_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10007** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10007/.well-known/agent-card.json
- Health Check: http://localhost:10007/health

## 更多信息

有关功能详细信息、筛选选项和故障排除，请参阅英文版 README。
