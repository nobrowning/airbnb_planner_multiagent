# Host Agent 架构重构说明

## 概述

将原来的 `host_router` 单一 agent 拆分为两个独立的专职 agent，并整合到 Orchestrator 的工作流中。

## 新架构

```
Orchestrator (SequentialAgent)
├── 1. PlanActions (Planner) - 任务规划
├── 2. SubAgentSearcher - Sub-Agent 发现
├── 3. SubAgentCaller - Sub-Agent 调用
└── 4. ResultSummarizer - 结果汇总
```

## 组件说明

### 1. PlanActions (Planner)
**职责**: 分析用户请求，生成结构化的任务计划

**输出**: 
- 保存到 `context.state['plan']`
- 包含：子任务列表、优先级、依赖关系、具体日期

### 2. SubAgentSearcher
**文件**: `sub_agent_searcher.py`

**职责**: 
- 接收 Planner 生成的计划
- 分析计划中的每个子任务
- 根据任务类型选择关键词 (weather, accommodations, tripadvisor, location, transport)
- 调用注册中心查找匹配的 sub-agents
- 将发现的 agents 信息保存到 state

**工具**:
- `search_agents(keyword, task, topk)`: 查询注册中心

**输出到 State**:
```python
state["discovered_agents"] = [
    {
        "name": "Weather Agent",
        "url": "http://...",
        "keyword": "weather",
        "task": "..."
    },
    # ...
]
state["registry_responses"] = {
    "weather": {"topk_list": [...], "agent_list": [...], "task": "..."},
    # ...
}
```

**特性**:
- 使用 `tool_context.actions.skip_summarization = True` 跳过 LLM 总结
- 直接返回 API 结果，提高效率

### 3. SubAgentCaller
**文件**: `sub_agent_caller.py`

**职责**:
- 读取 `discovered_agents` 信息
- 建立与这些 agents 的连接 (获取 agent card)
- 根据可用 agents 动态生成 instruction
- 提供 `send_message` 工具调用 sub-agents
- 收集所有响应

**生命周期**:
1. `before_model_callback`: 初始化连接
   - 读取 `state["discovered_agents"]`
   - 并发建立与所有 agents 的连接
   - 获取 agent cards
   - 更新 `available_agents_info`

2. `root_instruction`: 动态生成指令
   - 展示可用的 agents 列表
   - 提供调用示例
   - 包含原始计划上下文

3. LLM 执行: 调用 sub-agents
   - 使用 `send_message(agent_name, task)`
   - 可以并发或串行调用多个 agents

**工具**:
- `send_message(agent_name, task)`: 向指定 agent 发送任务

**输出到 State**:
```python
state["results"] = {
    "agent": "Weather Agent",
    "task": "...",
    "response": "...",
    "status": "success"
}
```

### 4. ResultSummarizer
**职责**: 汇总所有 sub-agent 的结果，生成最终用户友好的报告

## 数据流

```
User Query
    ↓
[Planner] 
    → state['plan'] = "1. Check weather 2. Find hotels..."
    ↓
[SubAgentSearcher]
    → search_agents("weather", "Check weather for LA", 3)
    → search_agents("accommodations", "Find hotels in LA", 3)
    → state['discovered_agents'] = [{name, url, keyword}, ...]
    ↓
[SubAgentCaller - before_model_callback]
    → Read state['discovered_agents']
    → Connect to each agent (fetch agent cards)
    → Build available_agents_info
    ↓
[SubAgentCaller - LLM execution]
    → Analyze plan and available agents
    → send_message("Weather Agent", "What's the weather...")
    → send_message("Airbnb Agent", "Find accommodations...")
    → state['results'] = {...}
    ↓
[ResultSummarizer]
    → Read state['results']
    → Synthesize and format
    → Generate final report
    ↓
Final Response to User
```

## 关键设计决策

### 1. 为什么拆分？
- **职责分离**: 搜索和调用是不同的关注点
- **可维护性**: 每个 agent 职责清晰，易于修改
- **可测试性**: 可以独立测试每个组件
- **可扩展性**: 可以轻松添加新的搜索策略或调用机制

### 2. 为什么 SubAgentSearcher 跳过总结？
```python
tool_context.actions.skip_summarization = True
```
- 注册中心返回的是结构化数据
- 不需要 LLM 二次处理
- 直接传递给下一个 agent 更高效
- 避免信息损失

### 3. 为什么使用 before_model_callback？
- 在 LLM 生成响应之前建立连接
- 确保 instruction 生成时连接已就绪
- 可以在 instruction 中展示可用 agents
- 让 LLM 感知到实际的运行时环境

### 4. 动态 Instruction 的价值
```python
def root_instruction(self, context: ReadonlyContext) -> str:
    # 根据实际连接的 agents 生成指令
    agent_roster_text = "\n".join([...])
    return f"Available agents: {agent_roster_text}"
```
- LLM 只看到实际可用的 agents
- 避免尝试调用不存在的 agents
- 指令始终与运行时状态一致

## 与原 host_router 的对比

| 特性 | 原 host_router | 新架构 (Searcher + Caller) |
|------|---------------|---------------------------|
| Agent 数量 | 1 个 | 2 个 |
| 职责划分 | 混合 (搜索+调用) | 清晰分离 |
| 并发查询注册中心 | ❌ | ✅ (Searcher) |
| 动态 Instruction | ⚠️ 部分 | ✅ 完全动态 |
| LLM 总结开销 | 较高 | 较低 (Searcher 跳过) |
| 可测试性 | 一般 | 优秀 |
| 状态管理 | 工具内部 | Context State |
| 扩展性 | 一般 | 优秀 |

## 使用示例

### 完整流程
```python
from orchestrator import orchestrator

# Orchestrator 已包含 4 个 sub-agents
runner = Runner(agent=orchestrator, ...)

# 用户查询
response = await runner.run_async(
    new_message="Plan a trip to Los Angeles this weekend"
)

# 内部流程：
# 1. Planner: 生成计划
# 2. Searcher: 查找 weather、accommodations、tripadvisor agents
# 3. Caller: 连接并调用这些 agents
# 4. Summarizer: 汇总结果
```

### 单独测试 SubAgentSearcher
```python
from sub_agent_searcher import create_sub_agent_searcher

searcher_agent = create_sub_agent_searcher()
# 测试注册中心查询...
```

### 单独测试 SubAgentCaller
```python
from sub_agent_caller import create_sub_agent_caller

caller_agent = create_sub_agent_caller()
# 测试 agent 调用...
```

## 配置要求

### 环境变量
```bash
# 注册中心地址
REGISTRY_BASE_URL=http://localhost:8000
```

### 依赖
- `google.adk`: Agent Development Kit
- `a2a`: Agent-to-Agent protocol
- `httpx`: HTTP 客户端
- `routing_agent`: 注册中心客户端

## 故障处理

### SubAgentSearcher 故障
- 注册中心不可用 → 返回空列表，记录错误
- 关键词无匹配 → 返回空列表，继续执行

### SubAgentCaller 故障
- 连接失败 → 跳过该 agent，记录错误
- Agent 响应超时 → 返回错误信息，继续其他 agents
- 部分 agents 失败 → 使用成功的结果继续

## 未来优化方向

1. **并发调用优化**: SubAgentCaller 可以并发调用多个 agents
2. **缓存机制**: 缓存 agent cards 避免重复获取
3. **重试逻辑**: 对失败的连接/调用进行重试
4. **监控指标**: 添加 agent 性能和可用性监控
5. **动态 topk**: 根据任务复杂度动态调整搜索数量

## 总结

新架构通过职责分离、状态管理和动态配置，提供了更清晰、可维护和可扩展的解决方案。每个 agent 专注于单一职责，通过 context.state 共享信息，形成了一个高效的协作系统。
