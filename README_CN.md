# 多智能体旅行规划系统

[English](README.md) | [中文文档](README_CN.md)

----
> **⚠️ 免责声明**：此演示仅用于演示目的，不适用于生产环境。
>
> **⚠️ 重要提示**：A2A 是一个正在开发中的项目(WIP)。在不久的将来可能会有与此处演示不同的变化。
>
> **⚠️ 安全提示**：在构建生产应用时，请将所有外部智能体视为潜在的不可信实体。所有从外部智能体接收的数据（包括 AgentCard、消息、工件和任务状态）都应作为不可信输入处理，并进行适当验证，以防止安全漏洞，如提示注入攻击。
----

这是一个基于 Agent2Agent (A2A) 协议和 Google Agent Development Kit (ADK) 构建的综合旅行规划系统。该系统具有一个Host智能体，可以智能协调 7 个专门的智能体，提供端到端的旅行规划服务，包括航班、酒店、Airbnb、天气、活动、景点、餐厅和金融信息。

## 🌟 主要特点

- **智能多智能体协调**：Host智能体协调 7 个专门的智能体
- **实时信息**：实时天气、航班价格、酒店可用性和活动列表
- **全面的旅行规划**：一站式解决所有旅行需求
- **交互式 Web 界面**：用户友好的 Gradio 聊天界面
- **A2A 协议**：行业标准的智能体间通信
- **MCP 集成**：模型上下文协议用于工具交互

## 🏗️ 系统架构

该系统采用中心辐射式架构，Host智能体协调所有专门的智能体：

```
┌──────────────────────────────────────────────────────────────┐
│                        用户界面                               │
│                   (Gradio Web UI - 端口 8083)                │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       Host智能体                             │
│                      智能请求路由器                           │
└──┬────────┬────────┬────────┬────────┬────────┬────────┬────┘
   │        │        │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼        ▼        ▼
┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐
│Weather││Airbnb ││ Trip  ││ Event ││Finance││Flight ││ Hotel │
│ 天气   ││爱彼迎  ││Advisor││ 活动  ││ 金融   ││ 航班   ││ 酒店   │
│ 10001 ││ 10002 ││ 猫途鹰 ││ 10004 ││ 10005 ││ 10006 ││ 10007 │
│       ││       ││ 10003 ││       ││       ││       ││       │
└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘
```

## 🤖 专门的智能体

### 1. **Host智能体 (Host Agent)** (端口 8083)
**用途**：中心协调智能体和用户界面

**功能**：
- 智能查询分析和路由到适当的专门智能体
- 多智能体响应协调和综合
- 带 Gradio Web UI 的实时流式界面
- 复杂多智能体查询分解
- 并行智能体执行以获得全面结果

**技术栈**：Google ADK、Gradio、A2A 协议、LiteLLM

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证

[文档](host_agent/README.md) | [中文文档](host_agent/README_CN.md)

---

### 2. **天气智能体 (Weather Agent)** (端口 10001)
**用途**：天气预报和气象信息

**功能**：
- 按位置查询当前天气状况
- 多日天气预报
- 全球城市覆盖
- 详细的气象数据（温度、湿度、降水概率）
- 天气警报和警告

**技术栈**：Google ADK、FastMCP、天气 API

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证

[文档](weather_agent/README.md) | [中文文档](weather_agent/README_CN.md)

---

### 3. **Airbnb 智能体** (端口 10002)
**用途**：Airbnb 住宿搜索和预订协助

**功能**：
- 按位置、日期和客人数量搜索 Airbnb 房源
- 按价格、评分和设施筛选
- 详细的房产信息（评论、照片、房东详情）
- 检查特定日期的可用性
- 支持各种房产类型

**技术栈**：Google ADK、LangGraph、MCP、React Agent

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证

[文档](airbnb_agent/README.md) | [中文文档](airbnb_agent/README_CN.md)

---

### 4. **猫途鹰智能体 (TripAdvisor Agent)** (端口 10003)
**用途**：景点和餐厅推荐

**功能**：
- 在猫途鹰上搜索地点和景点
- 查找附近的餐厅和用餐场所
- 详细的评论和评分信息
- 照片库和用户生成内容
- 支持全球主要旅游目的地

**技术栈**：Google ADK、FastMCP、TripAdvisor API

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证
- TripAdvisor API 密钥

[文档](tripadvisor_agent/README.md) | [中文文档](tripadvisor_agent/README_CN.md)

---

### 5. **活动智能体 (Event Agent)** (端口 10004)
**用途**：活动发现和活动规划

**功能**：
- 按位置、日期和类型搜索活动
- 多种日期过滤器（今天、明天、本周、周末、下周、本月、自定义日期）
- 按活动类别筛选（音乐会、节日、虚拟活动等）
- 详细的活动信息（场地、门票、时间、描述）
- 基于兴趣的活动推荐

**技术栈**：Google ADK、FastMCP、SerpAPI (Google Events)

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证
- SerpAPI 密钥

[文档](event_agent/README.md) | [中文文档](event_agent/README_CN.md)

---

### 6. **金融智能体 (Finance Agent)** (端口 10005)
**用途**：金融市场数据和货币转换

**功能**：
- 实时股票价格查询和报价
- 货币汇率转换（支持主要世界货币）
- 市场概况、趋势和指数
- 历史股票价格分析
- 股票价格变动比较和筛选

**技术栈**：Google ADK、FastMCP、SerpAPI (Google Finance)

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证
- SerpAPI 密钥

**免责声明**：提供的金融信息仅供参考，不构成财务建议。

[文档](finance_agent/README.md) | [中文文档](finance_agent/README_CN.md)

---

### 7. **航班智能体 (Flight Agent)** (端口 10006)
**用途**：航班搜索和比较

**功能**：
- 搜索往返、单程和多城市航班
- 跨航空公司和日期的价格比较
- 按价格、航空公司、中转和时长筛选
- 详细的航班信息（中转、飞机类型、行李政策）
- 根据价格/时长识别最佳价值航班
- 支持多种乘客类型和旅行舱位

**技术栈**：Google ADK、FastMCP、SerpAPI (Google Flights)

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证
- SerpAPI 密钥

[文档](flight_agent/README.md) | [中文文档](flight_agent/README_CN.md)

---

### 8. **酒店智能体 (Hotel Agent)** (端口 10007)
**用途**：酒店和住宿搜索

**功能**：
- 搜索多种住宿类型（酒店、度假村、度假租赁、公寓、民宿）
- 高级筛选（价格、评分、设施、星级、房产类型）
- 详细的房产信息（房型、设施、政策、评论）
- 跨房产的价格比较
- 免费取消和特价优惠筛选
- 位置分析和接近景点的距离

**技术栈**：Google ADK、FastMCP、SerpAPI (Google Hotels)

**API 要求**：
- Google Gemini API 密钥或 Vertex AI 凭证
- SerpAPI 密钥

[文档](hotel_agent/README.md) | [中文文档](hotel_agent/README_CN.md)

## 🚀 快速开始

### 前置要求

1. **Python 3.13+**（A2A SDK 要求）
2. **uv** - 快速 Python 包管理器
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **API 密钥**：
   - **Google Gemini API 密钥**（所有智能体必需）
     - 获取方式：https://makersuite.google.com/app/apikey
     - 或用于生产环境的 **Vertex AI 凭证**
   - **SerpAPI 密钥**（航班、酒店、活动、金融智能体必需）
     - 获取方式：https://serpapi.com/
   - **TripAdvisor API 密钥**（猫途鹰智能体必需）
     - 获取方式：https://www.tripadvisor.com/developers

### 安装

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd airbnb_planner_multiagent
   ```

2. **设置配置**

   复制示例配置文件：
   ```bash
   cp .env.example .env
   ```

3. **配置 .env 文件**

   编辑 `.env` 文件并配置您的凭证：

   **选项 A：Gemini 开发者 API（推荐用于开发）**
   ```env
   # Google Gemini API
   GOOGLE_API_KEY="your-api-key-here"
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   ```

   **选项 B：Vertex AI（推荐用于生产）**
   ```env
   # Vertex AI 配置
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT="your-project-id"
   GOOGLE_CLOUD_LOCATION="global"
   GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   GOOGLE_GENAI_MODEL="gemini-2.5-flash"
   ```

   **添加其他 API 密钥**：
   ```env
   # SerpAPI（航班、酒店、活动、金融智能体必需）
   SERPAPI_KEY=your_serpapi_key_here

   # TripAdvisor API（猫途鹰智能体必需）
   TRIPADVISOR_API_KEY=your_tripadvisor_api_key

   # 智能体 URL（默认端口 - 通常无需更改）
   WEA_AGENT_URL=http://localhost:10001
   AIR_AGENT_URL=http://localhost:10002
   TRI_AGENT_URL=http://localhost:10003
   EVE_AGENT_URL=http://localhost:10004
   FIN_AGENT_URL=http://localhost:10005
   FLI_AGENT_URL=http://localhost:10006
   HOT_AGENT_URL=http://localhost:10007

   # 应用设置
   APP_URL=http://127.0.0.1:8083
   ```

### 运行系统

系统由 **8 个智能体**组成，必须同时运行。Host（端口 8083）协调所有其他智能体，因此必须**最后**启动。

**选项 1：使用控制脚本自动启动（推荐）**

`agent_control.sh` 脚本为所有智能体提供统一管理：

```bash
# 按正确顺序启动所有智能体
./agent_control.sh start
# 或简单地：
./agent_control.sh

# 检查所有智能体的状态
./agent_control.sh status

# 查看所有日志文件
./agent_control.sh logs

# 查看特定智能体的日志
./agent_control.sh logs weather_agent

# 优雅地停止所有智能体
./agent_control.sh stop

# 清理日志文件
./agent_control.sh clean

# 显示帮助
./agent_control.sh help
```

**脚本的功能：**
1. 启动所有 7 个专门的智能体（天气、Airbnb、猫途鹰、活动、金融、航班、酒店）
2. 等待它们初始化（默认：5 秒）
3. 启动带 Gradio UI 的Host智能体
4. 在 `logs/` 目录中提供日志文件
5. 在 Ctrl+C 时处理优雅关闭

**选项 2：手动启动（用于开发/调试）**

在**单独的终端窗口**中启动每个智能体：

```bash
# 终端 1 - 天气智能体（端口 10001）
cd weather_agent && uv run .

# 终端 2 - Airbnb 智能体（端口 10002）
cd airbnb_agent && uv run .

# 终端 3 - 猫途鹰智能体（端口 10003）
cd tripadvisor_agent && uv run .

# 终端 4 - 活动智能体（端口 10004）
cd event_agent && uv run .

# 终端 5 - 金融智能体（端口 10005）
cd finance_agent && uv run .

# 终端 6 - 航班智能体（端口 10006）
cd flight_agent && uv run .

# 终端 7 - 酒店智能体（端口 10007）
cd hotel_agent && uv run .

# 终端 8 - Host智能体（端口 8083）- 必须最后启动
cd host_agent && uv run .
```

**⚠️ 重要提示**：在启动Host智能体之前，启动所有专门的智能体后等待 5-10 秒，以确保所有智能体完全初始化。

### 访问应用

所有智能体运行后，打开浏览器并访问：

**http://127.0.0.1:8083**

您应该看到 Gradio 聊天界面已准备好接受您的旅行规划查询。

## 💬 示例查询

### 天气查询
```
洛杉矶的天气怎么样？
查看下周巴黎的天气预报
```

### 住宿查询
```
找一个洛杉矶 4 月 15-18 日 2 位成人的房间
搜索纽约 200 美元以下的酒店
找巴厘岛带泳池的度假租赁
```

### 景点和餐厅查询
```
找巴黎的餐厅
给我看时代广场附近的景点
在东京可以做什么？
```

### 活动查询
```
找本周末纽约的音乐会
给我看下个月奥斯汀的节日
```

### 金融查询
```
将 1000 美元转换为欧元
AAPL 的股票价格是多少？
```

### 航班查询
```
找 12 月 15 日从洛杉矶到纽约的航班
比较去伦敦往返的价格
```

### 复杂的多智能体查询
```
规划一个 5 天的巴黎之旅，包括航班、酒店、景点和活动
找中央公园附近的住宿和餐厅
东京的天气如何，并找本周末的活动？
```

## 🔧 配置和管理

### 配置架构

系统使用**简化的两文件配置**：

1. **`.env`** - 应用配置（API 密钥、凭证、智能体 URL）
2. **`agent_control.sh`** - 统一控制脚本（智能体定义、端口和所有命令）

**优势**：
- ✅ **减少 70% 的文件** - 2 个文件而不是 4 个以上
- ✅ **无重复** - 端口和配置只定义一次
- ✅ **单一界面** - 一个命令完成所有操作
- ✅ **更易维护** - 在一个地方编辑配置
- ✅ **兼容** - 适用于 bash 3.2+

### 智能体控制脚本

`agent_control.sh` 脚本是所有操作的**统一控制中心**：

```bash
# 启动所有智能体（默认命令）
./agent_control.sh
./agent_control.sh start      # 明确启动

# 检查所有智能体的状态
./agent_control.sh status

# 查看日志
./agent_control.sh logs                # 列出所有可用日志
./agent_control.sh logs weather_agent  # 查看特定智能体日志
./agent_control.sh logs host_agent     # 查看Host智能体日志

# 优雅地停止所有智能体
./agent_control.sh stop

# 清理日志文件
./agent_control.sh clean

# 从旧配置迁移
./agent_control.sh migrate

# 显示帮助和可用命令
./agent_control.sh help
```

### 自定义智能体端口

要更改智能体端口或添加新智能体，请编辑 `agent_control.sh` 并修改 `AGENT_CONFIGS` 数组：

```bash
# 在 agent_control.sh 中
AGENT_CONFIGS=(
    "weather_agent:10001"
    "airbnb_agent:10002"
    "tripadvisor_agent:10003"
    "event_agent:10004"
    "finance_agent:10005"
    "flight_agent:10006"
    "hotel_agent:10007"
    "your_new_agent:10008"    # 在此处添加新智能体
)
```

在 `agent_control.sh` 中修改端口后，记得在 `.env` 中更新相应的 URL：

```env
YOUR_NEW_AGENT_URL=http://localhost:10008
```

### 调整定时参数

如果智能体需要更多时间启动，请在 `agent_control.sh` 中编辑定时变量：

```bash
# 在 agent_control.sh 中
AGENT_STARTUP_DELAY=1      # 启动每个子智能体之间的延迟（秒）
AGENT_INIT_WAIT=5          # 子智能体初始化的等待时间（秒）
HOST_STARTUP_WAIT=3        # 启动Host智能体后的等待时间（秒）
```

## 📊 系统状态和监控

### 检查智能体健康状况

访问智能体卡端点：
- 天气：http://localhost:10001/.well-known/agent-card.json
- Airbnb：http://localhost:10002/.well-known/agent-card.json
- 猫途鹰：http://localhost:10003/.well-known/agent-card.json
- 活动：http://localhost:10004/.well-known/agent-card.json
- 金融：http://localhost:10005/.well-known/agent-card.json
- 航班：http://localhost:10006/.well-known/agent-card.json
- 酒店：http://localhost:10007/.well-known/agent-card.json

### 查看日志

```bash
# 列出所有日志
./agent_control.sh logs

# 查看特定智能体日志
./agent_control.sh logs weather_agent

# 实时监控
tail -f logs/*.log
```

## 📁 项目结构

```
airbnb_planner_multiagent/
├── .env                      # 🔑 配置（API 密钥、凭证、智能体 URL）
├── .env.example              # 📝 配置模板
├── agent_control.sh          # 🎯 统一控制脚本（启动/停止/状态/日志）
├── migrate_config.sh         # 🔄 旧配置的迁移助手
├── README.md                 # 📖 项目文档（英文）
├── README_CN.md              # 📖 项目文档（中文）
├── CONFIG.md                 # ⚙️  配置指南（已合并到 README）
├── STARTUP.md                # 🚀 启动指南（已合并到 README）
├── CLAUDE.md                 # 🤖 Claude Code 指令
│
├── weather_agent/            # ☁️  天气智能体（端口 10001）
│   ├── weather_agent.py
│   ├── weather_executor.py
│   ├── weather_mcp.py       # 天气工具的 MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── airbnb_agent/            # 🏠 Airbnb 智能体（端口 10002）
│   ├── airbnb_agent.py      # LangGraph React 智能体
│   ├── agent_executor.py    # A2A 执行器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── tripadvisor_agent/       # 🗺️  猫途鹰智能体（端口 10003）
│   ├── tripadvisor_agent.py
│   ├── tripadvisor_executor.py
│   ├── tripadvisor_server/  # MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── event_agent/             # 🎉 活动智能体（端口 10004）
│   ├── event_agent.py
│   ├── event_executor.py
│   ├── event_server/        # SerpAPI 活动的 MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── finance_agent/           # 💰 金融智能体（端口 10005）
│   ├── finance_agent.py
│   ├── finance_executor.py
│   ├── finance_server/      # 金融数据的 MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── flight_agent/            # ✈️  航班智能体（端口 10006）
│   ├── flight_agent.py
│   ├── flight_executor.py
│   ├── flight_server/       # 航班搜索的 MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── hotel_agent/             # 🏨 酒店智能体（端口 10007）
│   ├── hotel_agent.py
│   ├── hotel_executor.py
│   ├── hotel_server/        # 酒店搜索的 MCP 服务器
│   ├── __main__.py
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
├── host_agent/              # 🎛️  Host智能体（端口 8083）
│   ├── routing_agent.py     # 主要路由逻辑
│   ├── remote_agent_connection.py  # A2A 客户端
│   ├── __main__.py          # Gradio UI
│   ├── .env → ../.env       # 使用根目录 .env
│   └── README.md
│
└── logs/                    # 📋 智能体日志（由 agent_control.sh 自动创建）
    ├── weather_agent.log
    ├── airbnb_agent.log
    ├── tripadvisor_agent.log
    ├── event_agent.log
    ├── finance_agent.log
    ├── flight_agent.log
    ├── hotel_agent.log
    └── host_agent.log
```

**关键文件：**
- **`.env`**：所有智能体的集中配置（API 密钥、URL、模型设置）
- **`agent_control.sh`**：用于所有操作的单一脚本（启动、停止、状态、日志）
- **`README_CN.md`**：综合文档（本文件）
- **`logs/`**：自动创建的目录，包含每个智能体的日志

## 🔐 安全考虑

**重要提示**：此演示仅用于演示目的。在构建生产应用时：

- ✅ 将所有外部智能体视为潜在的不可信实体
- ✅ 验证和清理所有接收到的数据
- ✅ 实施适当的身份验证和授权
- ✅ 使用安全的凭证管理（例如，密钥管理器）
- ✅ 在处理之前验证智能体卡和响应
- ✅ 实施速率限制和配额管理
- ✅ 监控可疑活动

**警告**：恶意智能体可能提供精心制作的数据，如果在 LLM 提示中使用而不进行清理，可能导致提示注入攻击。


## 📚 其他资源

### 项目文档
- **[README.md](README.md)** - 完整的项目文档（英文）
- **[README_CN.md](README_CN.md)** - 完整的项目文档（中文，本文件）
- **[CLAUDE.md](CLAUDE.md)** - Claude Code 指令
- **[.env.example](.env.example)** - 包含所有必需变量的配置模板
- **各智能体 README**：
  - [Host智能体](host_agent/README.md) | [中文](host_agent/README_CN.md)
  - [天气智能体](weather_agent/README.md) | [中文](weather_agent/README_CN.md)
  - [Airbnb 智能体](airbnb_agent/README.md) | [中文](airbnb_agent/README_CN.md)
  - [猫途鹰智能体](tripadvisor_agent/README.md) | [中文](tripadvisor_agent/README_CN.md)
  - [活动智能体](event_agent/README.md) | [中文](event_agent/README_CN.md)
  - [金融智能体](finance_agent/README.md) | [中文](finance_agent/README_CN.md)
  - [航班智能体](flight_agent/README.md) | [中文](flight_agent/README_CN.md)
  - [酒店智能体](hotel_agent/README.md) | [中文](hotel_agent/README_CN.md)

### 框架和协议文档
- **[A2A 协议](https://github.com/google/a2a-python)** - 智能体间通信协议
- **[Google ADK 文档](https://google.github.io/adk-docs/)** - 智能体开发工具包
- **[A2A 购物助手教程](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1)** - 动手实践 A2A 教程
- **[模型上下文协议 (MCP)](https://modelcontextprotocol.io/)** - 工具集成协议
- **[LangGraph 文档](https://langchain-ai.github.io/langgraph/)** - Airbnb 智能体中使用的智能体框架
- **[FastMCP 文档](https://github.com/jlowin/fastmcp)** - 快速 MCP 服务器框架

### API 文档和密钥
- **[Google Gemini API](https://makersuite.google.com/app/apikey)** - 获取您的 Gemini API 密钥
- **[Google Cloud 控制台](https://console.cloud.google.com/)** - 用于 Vertex AI 设置
- **[Vertex AI 文档](https://cloud.google.com/vertex-ai/docs)** - 生产 AI 平台
- **[SerpAPI](https://serpapi.com/)** - Google 搜索和数据 API
  - [SerpAPI 仪表板](https://serpapi.com/dashboard) - 管理 API 密钥和积分
  - [SerpAPI 文档](https://serpapi.com/docs) - API 参考
- **[TripAdvisor 开发者门户](https://www.tripadvisor.com/developers)** - 获取 TripAdvisor API 密钥

### 相关工具
- **[uv](https://github.com/astral-sh/uv)** - 快速 Python 包管理器
- **[Gradio](https://www.gradio.app/)** - Host智能体使用的 Web UI 框架
- **[LiteLLM](https://docs.litellm.ai/)** - 智能体中使用的多 LLM 代理

