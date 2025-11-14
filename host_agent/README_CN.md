# Host Agent - 旅行规划协调器

[English](README.md)

## Agent 简介

Host Agent 是旅行规划系统的中央调度智能体。它作为主入口，智能地将用户请求路由到各个专门的智能体（Weather、Airbnb、TripAdvisor、Events、Finance、Flights、Hotels），并协调它们的响应，提供全面的旅行规划解决方案。

**主要功能：**
- 智能分析用户查询并路由到合适的专业智能体
- 协调多个智能体的响应
- 提供友好的 Gradio Web 交互界面
- 支持复杂的多智能体查询
- 实时流式响应展示

**Web 界面端口：** `8083`

**调度智能体：**
- Weather Agent (10001) - 天气预报
- Airbnb Agent (10002) - Airbnb 房源搜索
- TripAdvisor Agent (10003) - 景点和餐厅推荐
- Event Agent (10004) - 活动搜索
- Finance Agent (10005) - 货币转换和金融数据
- Flight Agent (10006) - 航班搜索
- Hotel Agent (10007) - 酒店搜索

## 启动方式

### 配置要求

1. **复制环境配置文件**

   ```bash
   cd host_agent
   cp example.env .env
   ```

2. **配置 API Key 和智能体 URL**

   编辑 `.env` 文件，填入以下配置：

   ```env
   # Google Gemini API（必需）
   GOOGLE_API_KEY=your_google_api_key
   LITELLM_MODEL=gemini-2.5-flash

   # Vertex AI（可选）
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your_project_id
   GOOGLE_CLOUD_LOCATION=global
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

   # 各智能体的 URL（根据实际端口配置）
   WEA_AGENT_URL=http://localhost:10001
   AIR_AGENT_URL=http://localhost:10002
   TRI_AGENT_URL=http://localhost:10003
   EVE_AGENT_URL=http://localhost:10004
   FIN_AGENT_URL=http://localhost:10005
   FLI_AGENT_URL=http://localhost:10006
   HOT_AGENT_URL=http://localhost:10007

   # 远程智能体 API Keys（可选）
   # 为需要认证的智能体设置 API key
   AIRBNB_API_KEY=your-airbnb-agent-api-key-here

   # 应用设置
   APP_URL=http://127.0.0.1:8083
   ```

   **获取 API Key：**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - Vertex AI: 需要设置 Google Cloud 项目
   
   **智能体认证：**
   - 如果某个远程智能体（例如 Airbnb Agent）需要 API key 认证，在 `.env` 中设置相应的 API key
   - Host Agent 将在与需要认证的智能体通信时自动包含 API key

### 启动命令

**重要：** 在启动 Host Agent 之前，需要先启动所有专业智能体。

1. **启动所有专业智能体**（在不同的终端窗口中）

   ```bash
   # 终端 1 - Weather Agent
   cd weather_agent && uv run .
   
   # 终端 2 - Airbnb Agent
   cd airbnb_agent && uv run .
   
   # 终端 3 - TripAdvisor Agent
   cd tripadvisor_agent && uv run .
   
   # 终端 4 - Event Agent
   cd event_agent && uv run .
   
   # 终端 5 - Finance Agent
   cd finance_agent && uv run .
   
   # 终端 6 - Flight Agent
   cd flight_agent && uv run .
   
   # 终端 7 - Hotel Agent
   cd hotel_agent && uv run .
   ```

2. **启动 Host Agent**

   ```bash
   cd host_agent
   uv run .
   ```

启动成功后，打开浏览器访问：**http://127.0.0.1:8083**

### 验证运行状态

检查各智能体是否正常运行，访问它们的 Agent Card：
- Weather: http://localhost:10001/.well-known/agent-card.json
- Airbnb: http://localhost:10002/.well-known/agent-card.json
- TripAdvisor: http://localhost:10003/.well-known/agent-card.json
- Event: http://localhost:10004/.well-known/agent-card.json
- Finance: http://localhost:10005/.well-known/agent-card.json
- Flight: http://localhost:10006/.well-known/agent-card.json
- Hotel: http://localhost:10007/.well-known/agent-card.json

## 智能体认证

某些远程智能体可能需要 API key 认证来进行访问控制。Host Agent 支持使用 Bearer token 认证连接到受保护的智能体。

**工作原理：**
1. 如果远程智能体需要认证（例如 Airbnb Agent），在 `.env` 中设置其 API key
2. Host Agent 将在获取 agent card 和与该智能体通信时自动包含 `Authorization: Bearer <api-key>` 头
3. 使用智能体 URL 来匹配 API key（例如，`http://localhost:10002` 对应 `AIRBNB_API_KEY`）

**支持认证的智能体：**
- **Airbnb Agent**：如果 Airbnb Agent 启用了认证，请设置 `AIRBNB_API_KEY`

**添加更多认证智能体：**
要为其他智能体添加认证，编辑 `routing_agent.py` 并添加 API key 映射：
```python
# 在 _get_initialized_routing_agent_sync() 中
weather_api_key = os.getenv('WEATHER_API_KEY')
weather_url = os.getenv('WEA_AGENT_URL', 'http://localhost:10001')
if weather_api_key:
    agent_api_keys[weather_url] = weather_api_key
```

## 使用方法

1. 打开浏览器访问 `http://127.0.0.1:8083`
2. 在聊天界面中输入您的旅行规划查询
3. Host Agent 将自动路由到合适的代理
4. 实时查看响应和工具调用
5. 提出后续问题或优化请求

## 支持的查询类型

### 天气查询
```
洛杉矶的天气怎么样？
查看巴黎下周的天气预报
```

### 住宿查询
```
找一个4月15-18日在洛杉矶的房间，2个成人
在纽约找一个200美元以下的酒店
在巴厘岛找有泳池的度假租房
```

### 景点和餐厅查询
```
巴黎有什么餐厅？
时代广场附近的景点
东京有什么好玩的？
```

### 活动查询
```
本周末纽约有什么音乐会？
奥斯汀下个月有什么节日？
```

### 金融查询
```
1000美元兑换成欧元是多少？
AAPL股价多少？
```

### 航班查询
```
12月15日从洛杉矶飞往纽约的航班
比较往返伦敦的价格
```

### 复杂的多智能体查询
```
规划一个5天的巴黎之行，包括航班、酒店、景点和活动
找中央公园附近的住宿和餐厅
```

## 更多信息

有关架构详细信息、错误处理和开发指南，请参阅英文版 README。
