# Airbnb Agent

[English](README.md)

## Agent 简介

Airbnb Agent 是一个专门用于搜索 Airbnb 房源的智能体。它集成了 Google Agent Development Kit (ADK) 和 LangGraph，通过 A2A（Agent-to-Agent）协议与其他智能体进行通信，帮助用户查找和筛选合适的住宿选项。

**主要功能：**
- 基于位置、日期、人数搜索 Airbnb 房源
- 提供房源详细信息（价格、评分、设施等）
- 支持按价格、评分等条件筛选
- 返回房源链接、图片和评价信息

**端口：** `10002`

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd airbnb_agent
   cp "example copy.env" .env
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
cd airbnb_agent
uv run .
```

启动成功后，Agent 将在 **http://0.0.0.0:10002** 上运行。

### 验证运行状态

访问以下 URL 检查 Agent 是否正常运行：
- Agent Card: http://localhost:10002/.well-known/agent-card.json
- Health Check: http://localhost:10002/health

## 免责声明

重要提示：提供的示例代码仅用于演示目的，展示了 Agent-to-Agent (A2A) 协议的机制。在构建生产应用程序时，将任何不在您直接控制下的代理视为潜在的不可信实体至关重要。

从外部代理接收的所有数据，包括但不限于其 AgentCard、消息、工件和任务状态，都应作为不可信输入处理。例如，恶意代理可能会提供包含精心设计数据的 AgentCard（例如 description、name、skills.description）。如果在未经清理的情况下使用这些数据来构造大型语言模型 (LLM) 的提示，可能会使您的应用程序遭受提示注入攻击。未能在使用前正确验证和清理这些数据可能会给您的应用程序带来安全漏洞。

开发人员有责任实施适当的安全措施，例如输入验证和凭据的安全处理，以保护其系统和用户。
