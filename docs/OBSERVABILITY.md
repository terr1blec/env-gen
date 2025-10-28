# 可观测性功能文档

## 概述

MCP Workflow 现在包含强大的可观测性功能，包括：

1. **实时进度可视化** - 使用 Rich 库的漂亮终端UI
2. **Agent决策过程追踪** - 详细记录所有决策和工具调用
3. **结构化事件日志** - 自动保存 JSONL 格式的追踪文件
4. **性能统计** - 追踪每个阶段的执行时间和资源使用

## 功能特性

### 1. 实时进度可视化

#### 显示内容
- **工作流阶段表格**：显示所有阶段的状态、持续时间、轮次和工具调用统计
- **实时工具调用树**：显示最近的5个工具调用
- **进度条**：显示整体完成进度
- **彩色状态图标**：
  - ⏳ 待处理 (Pending)
  - ▶️ 进行中 (In Progress)
  - ✅ 已完成 (Completed)
  - ❌ 失败 (Failed)
  - ⏭️ 跳过 (Skipped)

#### 示例输出
```
╭───────────────────────────────────────────────────────────────────╮
│ 🚀 MCP Workflow Execution  |  Elapsed: 2m 34s                     │
╰───────────────────────────────────────────────────────────────────╯

╭─ Workflow Stages ─────────────────────────────────────────────────╮
│ Stage                     Status          Duration   Turns  Tools │
│ 📋 Schema Planning        ✅ completed    12.3s      3      5     │
│ 🗄️ Database Generation   ✅ completed    45.2s      8      12    │
│ ▶️ Database Execution     ✅ completed    8.1s       2      3     │
│ ⚙️ Server Implementation   ▶️ in_progress  15.4s      5      8     │
│ 👀 Code Review            ⏳ pending      -          -      -     │
│ 🧪 Integration Testing    ⏳ pending      -          -      -     │
╰───────────────────────────────────────────────────────────────────╯

╭─ Recent Tool Calls ───────────────────────────────────────────────╮
│ 🔧 Tool Activity                                                   │
│ ├── 14:32:15 [Server Builder] → write_text                        │
│ ├── 14:32:12 [Server Builder] → read_text                         │
│ ├── 14:32:10 [Server Builder] → get_recommended_paths             │
│ ├── 14:32:08 [Server Builder] → get_notes                         │
│ └── 14:32:05 [Database Executor] → run_python                     │
╰───────────────────────────────────────────────────────────────────╯

Workflow Progress ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50% 0:02:34
```

### 2. Agent决策过程追踪

#### ObservabilityTracker

追踪所有重要事件：

```python
from workflow.observability import ObservabilityTracker, EventType

# 自动创建并传递给工作流
tracker = ObservabilityTracker(context)

# 追踪的事件类型：
# - AGENT_START / AGENT_END: Agent 开始和结束
# - AGENT_TURN: Agent 执行轮次
# - TOOL_CALL / TOOL_RESULT: 工具调用及结果
# - DECISION_POINT: 重要决策点
# - VALIDATION: 验证检查
# - ERROR: 错误事件
# - NOTE: 一般注释
```

#### 事件记录示例

```python
# 自动记录 Agent 开始
tracker.start_agent(
    agent_name="Schema Planner",
    step_name="schema_planning",
    prompt="Analyze schema..."
)

# 自动记录工具调用
tracker.record_tool_call(
    step_name="schema_planning",
    tool_name="describe_schema",
    tool_args={}
)

# 记录决策点
tracker.record_decision(
    step_name="code_review_cycle_1",
    decision="REVISIONS_NEEDED",
    reasoning="Database structure mismatch"
)

# 记录验证结果
tracker.record_validation(
    validation_type="database_contract",
    success=True,
    message="All keys validated",
    details={"expected_keys": ["users", "posts"]}
)
```

### 3. 追踪文件输出

#### 实时追踪 (JSONL)
每个事件实时写入 `logs/{domain}/{slug}/trace_YYYYMMDD_HHMMSS.jsonl`

```jsonl
{"timestamp": 1234567890.123, "event_type": "agent_start", "agent_name": "Schema Planner", "step_name": "schema_planning", ...}
{"timestamp": 1234567890.456, "event_type": "tool_call", "tool_name": "describe_schema", "tool_args": {}, ...}
{"timestamp": 1234567890.789, "event_type": "tool_result", "tool_name": "describe_schema", "tool_duration": 0.333, ...}
```

#### 完整追踪摘要 (JSON)
工作流结束后导出完整摘要到 `logs/{domain}/{slug}/trace_summary_{slug}.json`

```json
{
  "workflow_slug": "google-calendar",
  "start_time": 1234567890.0,
  "summary": {
    "total_duration": 154.3,
    "formatted_duration": "2m 34s",
    "total_events": 142,
    "total_agents": 6,
    "tool_calls_by_agent": {
      "Schema Planner": 5,
      "Database Synthesizer": 12,
      "Database Executor": 3,
      "Server Builder": 18,
      "Code Reviewer": 7,
      "Test Agent": 9
    },
    "traces": {
      "schema_planning": {
        "agent_name": "Schema Planner",
        "duration": 12.3,
        "turns": 3,
        "tool_calls_count": 5,
        "decisions_count": 1
      },
      ...
    }
  },
  "events": [...]
}
```

## 使用方法

### 启用/禁用进度可视化

默认启用，可以通过命令行参数禁用：

```bash
# 默认启用进度可视化
python main.py --schema "path/to/schema.json"

# 禁用进度可视化
python main.py --schema "path/to/schema.json" --no-progress
```

在代码中使用：

```python
from workflow import run_workflow

# args.enable_progress 会自动从命令行参数获取
await run_workflow(args)
```

### 无 Rich 库时的回退

如果没有安装 `rich` 库，系统会自动使用简单的文本进度追踪：

```
============================================================
🚀 MCP Workflow Execution Started
============================================================

▶️  schema_planning: Starting...
   🔧 [Schema Planner] describe_schema
   🔧 [Schema Planner] get_recommended_paths
✅ schema_planning: Completed

▶️  database_generation_cycle_1: Starting...
   🔧 [Database Synthesizer] write_text
...
```

### 访问追踪数据

#### 在运行时访问

```python
from workflow import run_workflow, ObservabilityTracker

# 运行工作流
summary = await run_workflow(args)

# 访问追踪器 (如果需要)
tracker = context._tracker

# 获取摘要
summary_data = tracker.get_summary()
print(f"Total events: {summary_data['total_events']}")
print(f"Duration: {summary_data['formatted_duration']}")

# 导出到自定义位置
tracker.export_trace(Path("my_custom_trace.json"))
```

#### 分析追踪文件

```python
import json

# 读取实时追踪 (JSONL)
with open("logs/domain/slug/trace_20250101_120000.jsonl") as f:
    for line in f:
        event = json.loads(line)
        if event["event_type"] == "tool_call":
            print(f"Tool: {event['tool_name']}, Args: {event['tool_args']}")

# 读取完整摘要
with open("logs/domain/slug/trace_summary_slug.json") as f:
    trace = json.load(f)
    
    # 分析工具使用情况
    for agent, count in trace["summary"]["tool_calls_by_agent"].items():
        print(f"{agent}: {count} tool calls")
    
    # 分析性能
    for step_name, trace_data in trace["summary"]["traces"].items():
        print(f"{step_name}: {trace_data['formatted_duration']}")
```

## 高级功能

### 自定义事件记录

你可以在代码中添加自定义事件：

```python
# 在 orchestrator.py 或其他模块中
if tracker:
    tracker.record_note(
        "Custom checkpoint reached",
        metadata={"checkpoint_id": "pre_validation", "data": {...}}
    )
```

### 决策点追踪

关键决策自动记录：

- Code Review 的 APPROVED/REVISIONS_NEEDED 判决
- 数据库是否需要重新生成
- 验证成功/失败

```python
# 示例：自动记录的决策
tracker.record_decision(
    step_name="code_review_cycle_1",
    decision="REVISIONS_NEEDED",
    reasoning="Review cycle 1 requested 3 revisions"
)
```

### 验证追踪

所有验证步骤自动记录：

```python
# 数据库契约验证
tracker.record_validation(
    validation_type="database_contract",
    success=True,
    message="Validated database JSON against DATA CONTRACT (2 keys)",
    details={"expected_keys": ["users", "posts"]}
)

# 元数据工具验证
tracker.record_validation(
    validation_type="metadata_tools",
    success=True,
    message="Validated metadata tool coverage (5 tools)",
    details={
        "expected_tools": ["get_events", "create_event", ...],
        "observed_tools": ["get_events", "create_event", ...]
    }
)
```

## 性能影响

- **实时可视化**: 约 1-2% 的性能开销（主要是终端刷新）
- **事件追踪**: 约 0.5% 的性能开销（异步写入文件）
- **内存使用**: 每个事件约 1-2KB，10000 个事件约 10-20MB

如果需要最大性能，可以禁用进度可视化：
```bash
python main.py --no-enable-progress
```

## 故障排除

### Rich 库未安装

```bash
# 安装依赖
pip install rich>=13.7.0

# 或使用 uv
uv pip install rich>=13.7.0
```

### 追踪文件未生成

检查 `logs_dir` 是否存在且有写入权限：

```python
# 在 context 初始化后
print(f"Logs directory: {context.logs_dir}")
print(f"Logs directory exists: {context.logs_dir.exists()}")
```

### 进度显示错乱

如果终端不支持 ANSI 颜色或 Unicode：

```bash
# 使用简单模式
python main.py --enable-progress false
```

或设置环境变量：

```bash
export TERM=dumb
python main.py
```

## 示例：完整的观测流程

```python
from workflow import run_workflow, ObservabilityTracker
import asyncio

async def main():
    # 配置参数
    args = parse_args()
    
    # 运行工作流（自动启用观测）
    summary = await asyncio.run(run_workflow(args))
    
    # 工作流完成后，追踪文件已自动保存
    # 查看实时追踪：logs/{domain}/{slug}/trace_*.jsonl
    # 查看完整摘要：logs/{domain}/{slug}/trace_summary_*.json
    
    print("Workflow completed with observability!")

if __name__ == "__main__":
    asyncio.run(main())
```

## 总结

新的可观测性功能为 MCP Workflow 提供了：

✅ **实时可见性** - 随时了解工作流执行状态  
✅ **详细追踪** - 记录每个决策和工具调用  
✅ **性能分析** - 识别瓶颈和优化机会  
✅ **调试支持** - 快速定位问题  
✅ **无侵入性** - 自动集成，无需修改现有代码  

开始使用吧！ 🚀

