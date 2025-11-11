# Flight Agent

[English](README.md)

## Agent 简介

Flight Agent 是一个专门用于搜索航班、比较价格和规划航空旅行的智能体。通过集成 Google Flights 和 SerpAPI，它能帮助用户查找往返、单程和多城市航班，提供全面的价格和航班时刻表信息。

**主要功能：**
- 搜索往返、单程和多城市航班
- 比较不同航空公司的价格和航班时间
- 按价格、航空公司、中转次数、飞行时长筛选航班
- 提供航班详细信息（中转、机型、行李政策等）
- 识别最佳性价比航班

**端口：** `10006`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd flight_agent
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
cd flight_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10006** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10006/.well-known/agent-card.json
- Health Check: http://localhost:10006/health

## 更多信息

有关功能详细信息、API 端点和故障排除，请参阅英文版 README。
