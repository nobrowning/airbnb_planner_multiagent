# Weather Agent

[English](README.md)

## Agent 简介

Weather Agent 是一个专门提供天气信息的智能体。它基于 Google Agent Development Kit (ADK) 构建，通过 A2A（Agent-to-Agent）协议与其他智能体进行通信，为用户提供准确的天气预报和气象信息。

**主要功能：**
- 查询指定地点的当前天气状况
- 提供未来几天的天气预报
- 支持全球主要城市的天气查询
- 返回温度、湿度、降水概率等详细气象数据

**端口：** `10001`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd weather_agent
   cp example.env .env
   ```

2. **配置 API Key**

   编辑 `.env` 文件，填入以下配置：

   ```env
   # 使用 Gemini Developer API
   GOOGLE_API_KEY="your_google_api_key"

   # 或者使用 Vertex AI
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT="your_project_id"
   GOOGLE_CLOUD_LOCATION="global"
   ```

   **获取 API Key：**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - Vertex AI: 需要设置 Google Cloud 项目

### 启动命令

```bash
cd weather_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10001** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10001/.well-known/agent-card.json
- Health Check: http://localhost:10001/health
