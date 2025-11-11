# Event Agent

[English](README.md)

## Agent 简介

Event Agent 是一个专门用于搜索和发现活动的智能体。通过集成 Google Events 和 SerpAPI，它能帮助用户查找音乐会、节日庆典、艺术展览和其他各类活动信息。

**主要功能：**
- 按地点、日期、类型搜索活动
- 支持多种日期筛选（今天、明天、本周、周末、下周、本月或自定义日期）
- 按活动类别筛选（音乐会、节日、虚拟活动等）
- 提供活动详细信息（场馆、票务、时间、描述）
- 发现基于用户兴趣的活动

**端口：** `10004`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd event_agent
   cp example.env .env
   ```

2. **配置 API Key**

   编辑 `.env` 文件，填入以下配置：

   ```env
   # Google Gemini API（必需）
   GOOGLE_API_KEY=your_google_api_key_here
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
cd event_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10004** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10004/.well-known/agent-card.json
- Health Check: http://localhost:10004/health

## 更多信息

有关功能详细信息、MCP 服务器工具和故障排除，请参阅英文版 README。
