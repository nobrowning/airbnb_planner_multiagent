# TripAdvisor Agent

[English](README.md)

## Agent 简介

TripAdvisor Agent 是一个专门用于搜索 TripAdvisor 景点、餐厅和评论的智能体。它基于 A2A 框架和 MCP 协议构建，帮助用户发现旅游景点、餐饮场所并查看详细评价信息。

**主要功能：**
- 搜索 TripAdvisor 上的地点和景点
- 查找附近的景点和餐厅
- 获取详细的地点信息和用户评论
- 查看照片和评分信息
- 支持全球主要旅游目的地

**端口：** `10003`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd tripadvisor_agent
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

   # TripAdvisor API（必需）
   TRIPADVISOR_API_KEY=your_tripadvisor_api_key
   ```

   **获取 API Key：**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - TripAdvisor API Key: https://www.tripadvisor.com/developers

### 启动命令

```bash
cd tripadvisor_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10003** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10003/.well-known/agent-card.json
- Health Check: http://localhost:10003/health

## 更多信息

有关功能详细信息和示例查询，请参阅英文版 README。
