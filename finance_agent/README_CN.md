# Finance Agent

[English](README.md)

## Agent 简介

Finance Agent 是一个专门提供金融市场信息的智能体。通过集成 Google Finance 和 SerpAPI，它能提供实时股票行情、货币汇率转换和金融市场分析数据。

**主要功能：**
- 实时股票价格查询
- 货币汇率转换（支持主要世界货币）
- 市场概览和指数趋势
- 历史股价分析
- 股票价格变动比较

**端口：** `10005`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd finance_agent
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
cd finance_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10005** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10005/.well-known/agent-card.json
- Health Check: http://localhost:10005/health

## 免责声明

**重要提示**：此代理提供的金融信息仅供参考。这不是财务建议，不应作为投资决策的唯一依据。在做出投资决定前，请务必咨询合格的财务顾问。
