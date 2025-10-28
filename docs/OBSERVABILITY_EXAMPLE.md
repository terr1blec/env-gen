# 可观测性使用示例

## 示例 1: 基本使用

最简单的使用方式 - 无需修改任何代码，自动启用：

```bash
# 运行工作流（自动启用可观测性）
python main.py --schema "mcp_servers/Time & Calendar/google-calendar.json"
```

你会看到实时的进度界面：

```
╭────────────────────────────────────────────────────────────╮
│ 🚀 MCP Workflow Execution  |  Elapsed: 1m 23s              │
╰────────────────────────────────────────────────────────────╯

╭─ Workflow Stages ──────────────────────────────────────────╮
│ Stage                     Status        Duration  Turns    │
│ 📋 Schema Planning        ✅ completed  15s       4        │
│ 🗄️ Database Generation   ▶️ in_progress 38s      7        │
│ ▶️ Database Execution     ⏳ pending     -        -        │
│ ⚙️ Server Implementation   ⏳ pending     -        -        │
│ 👀 Code Review            ⏳ pending     -        -        │
│ 🧪 Integration Testing    ⏳ pending     -        -        │
╰────────────────────────────────────────────────────────────╯

╭─ Recent Tool Calls ────────────────────────────────────────╮
│ 🔧 Tool Activity                                            │
│ ├── 14:32:15 [Database Synthesizer] → write_text          │
│ ├── 14:32:12 [Database Synthesizer] → get_notes           │
│ └── 14:32:10 [Schema Planner] → record_note               │
╰────────────────────────────────────────────────────────────╯
```

## 示例 2: 禁用可视化（仅日志）

如果你的终端不支持富文本或你更喜欢简单日志：

```bash
python main.py \
  --schema "mcp_servers/Social_Media/twitter.json" \
  --no-progress
```

输出会是简单的文本格式：

```
============================================================
🚀 MCP Workflow Execution Started
============================================================

▶️  schema_planning: Starting Schema Planner...
   🔧 [Schema Planner] describe_schema
   🔧 [Schema Planner] get_recommended_paths
   🔧 [Schema Planner] record_note
✅ schema_planning: Completed

▶️  database_generation_cycle_1: Starting Database Synthesizer...
   🔧 [Database Synthesizer] get_notes
   🔧 [Database Synthesizer] write_text
...
```

## 示例 3: 分析追踪数据

工作流完成后，分析生成的追踪文件：

```python
#!/usr/bin/env python3
"""分析工作流追踪数据的脚本"""

import json
from pathlib import Path
from collections import Counter

def analyze_trace(trace_file: Path):
    """分析追踪摘要文件"""
    with open(trace_file) as f:
        trace = json.load(f)
    
    summary = trace["summary"]
    
    print("="*60)
    print(f"Workflow: {trace['workflow_slug']}")
    print(f"Duration: {summary['formatted_duration']}")
    print(f"Total Events: {summary['total_events']}")
    print("="*60)
    
    # Agent 性能分析
    print("\n📊 Agent Performance:")
    for step_name, data in summary["traces"].items():
        print(f"  {step_name}:")
        print(f"    ⏱️  Duration: {data['formatted_duration']}")
        print(f"    🔄 Turns: {data['turns']}")
        print(f"    🔧 Tool Calls: {data['tool_calls_count']}")
    
    # 工具使用统计
    print("\n🔧 Tool Usage by Agent:")
    for agent, count in summary["tool_calls_by_agent"].items():
        print(f"  {agent}: {count} calls")
    
    # 分析事件类型
    event_types = Counter(event["event_type"] for event in trace["events"])
    print("\n📝 Event Type Distribution:")
    for event_type, count in event_types.most_common():
        print(f"  {event_type}: {count}")

# 使用示例
trace_file = Path("logs/time-calendar/google-calendar/trace_summary_google-calendar.json")
if trace_file.exists():
    analyze_trace(trace_file)
else:
    print(f"Trace file not found: {trace_file}")
```

运行脚本：

```bash
python analyze_trace.py
```

输出：

```
============================================================
Workflow: google-calendar
Duration: 3m 45s
Total Events: 287
============================================================

📊 Agent Performance:
  schema_planning:
    ⏱️  Duration: 18s
    🔄 Turns: 4
    🔧 Tool Calls: 5
  database_generation_cycle_1:
    ⏱️  Duration: 52s
    🔄 Turns: 9
    🔧 Tool Calls: 15
  database_sampling_cycle_1:
    ⏱️  Duration: 12s
    🔄 Turns: 3
    🔧 Tool Calls: 4
  server_generation_cycle_1:
    ⏱️  Duration: 68s
    🔄 Turns: 12
    🔧 Tool Calls: 22
  code_review_cycle_1:
    ⏱️  Duration: 34s
    🔄 Turns: 6
    🔧 Tool Calls: 8
  integration_tests:
    ⏱️  Duration: 41s
    🔄 Turns: 7
    🔧 Tool Calls: 11

🔧 Tool Usage by Agent:
  Schema Planner: 5
  Database Synthesizer: 15
  Database Executor: 4
  Server Builder: 22
  Code Reviewer: 8
  Test Agent: 11

📝 Event Type Distribution:
  tool_call: 65
  tool_result: 65
  agent_start: 6
  agent_end: 6
  agent_turn: 41
  validation: 8
  decision_point: 2
  note: 94
```

## 示例 4: 实时监控工具调用

监控实时追踪文件（JSONL 格式）：

```python
#!/usr/bin/env python3
"""实时监控工具调用的脚本"""

import json
import time
from pathlib import Path

def monitor_tool_calls(trace_file: Path):
    """实时监控工具调用"""
    print("🔍 Monitoring tool calls (Ctrl+C to stop)...\n")
    
    # 找到最新的追踪文件
    logs_dir = trace_file.parent
    if logs_dir.exists():
        trace_files = sorted(logs_dir.glob("trace_*.jsonl"))
        if trace_files:
            trace_file = trace_files[-1]
    
    if not trace_file.exists():
        print(f"Waiting for trace file: {trace_file}")
        while not trace_file.exists():
            time.sleep(1)
    
    print(f"Monitoring: {trace_file}\n")
    
    # 从头读取并持续监控新行
    with open(trace_file, 'r') as f:
        # 读取已有内容
        for line in f:
            event = json.loads(line)
            if event["event_type"] == "tool_call":
                print_tool_call(event)
        
        # 持续监控新内容
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            event = json.loads(line)
            if event["event_type"] == "tool_call":
                print_tool_call(event)

def print_tool_call(event):
    """格式化打印工具调用"""
    timestamp = event["formatted_timestamp"]
    agent = event.get("agent_name", "Unknown")
    tool = event["tool_name"]
    args = event.get("tool_args", {})
    
    # 简化参数显示
    args_str = ", ".join(f"{k}={v}" for k, v in list(args.items())[:2])
    if len(args) > 2:
        args_str += ", ..."
    
    print(f"[{timestamp}] {agent:20s} → {tool:20s}  ({args_str})")

# 使用示例
try:
    trace_file = Path("logs/time-calendar/google-calendar/trace_20250101_120000.jsonl")
    monitor_tool_calls(trace_file)
except KeyboardInterrupt:
    print("\n\n✅ Monitoring stopped")
```

运行：

```bash
python monitor_tools.py
```

输出：

```
🔍 Monitoring tool calls (Ctrl+C to stop)...

Monitoring: logs/time-calendar/google-calendar/trace_20250101_120000.jsonl

[2025-01-01 12:00:15.123] Schema Planner       → describe_schema      ()
[2025-01-01 12:00:16.456] Schema Planner       → get_recommended_paths()
[2025-01-01 12:00:18.789] Schema Planner       → record_note          (note=DATA CONTRACT...)
[2025-01-01 12:00:32.123] Database Synthesizer → get_notes            ()
[2025-01-01 12:00:35.456] Database Synthesizer → write_text           (relative_path=google_calendar_database.py, ...)
[2025-01-01 12:00:48.789] Database Synthesizer → write_text           (relative_path=google_calendar_database.json, ...)
...
```

## 示例 5: 决策点分析

提取和分析所有决策点：

```python
#!/usr/bin/env python3
"""分析工作流中的决策点"""

import json
from pathlib import Path

def analyze_decisions(trace_file: Path):
    """分析决策点"""
    with open(trace_file) as f:
        trace = json.load(f)
    
    decisions = [
        event for event in trace["events"]
        if event["event_type"] == "decision_point"
    ]
    
    print(f"📋 Found {len(decisions)} decision points:\n")
    
    for i, decision in enumerate(decisions, 1):
        print(f"{i}. {decision['decision']}")
        print(f"   Step: {decision['step_name']}")
        print(f"   Time: {decision['formatted_timestamp']}")
        if decision.get("reasoning"):
            print(f"   Reason: {decision['reasoning']}")
        print()

# 使用
trace_file = Path("logs/time-calendar/google-calendar/trace_summary_google-calendar.json")
analyze_decisions(trace_file)
```

输出：

```
📋 Found 2 decision points:

1. REVISIONS_NEEDED
   Step: code_review_cycle_1
   Time: 2025-01-01 12:03:45.123
   Reason: Review cycle 1 requested 3 revisions

2. APPROVED
   Step: code_review_cycle_2
   Time: 2025-01-01 12:05:23.456
   Reason: Code review passed all checks
```

## 示例 6: 验证失败分析

查找所有验证失败：

```python
#!/usr/bin/env python3
"""查找验证失败"""

import json
from pathlib import Path

def find_validation_failures(trace_file: Path):
    """查找验证失败"""
    with open(trace_file) as f:
        trace = json.load(f)
    
    validations = [
        event for event in trace["events"]
        if event["event_type"] == "validation"
    ]
    
    failures = [v for v in validations if not v["metadata"]["success"]]
    successes = [v for v in validations if v["metadata"]["success"]]
    
    print(f"✅ Successful validations: {len(successes)}")
    print(f"❌ Failed validations: {len(failures)}\n")
    
    if failures:
        print("Failed Validations:")
        for failure in failures:
            print(f"  ❌ {failure['metadata']['validation_type']}")
            print(f"     {failure['message']}")
            if failure["metadata"].get("details"):
                print(f"     Details: {failure['metadata']['details']}")
            print()

# 使用
trace_file = Path("logs/time-calendar/google-calendar/trace_summary_google-calendar.json")
find_validation_failures(trace_file)
```

## 示例 7: 性能瓶颈识别

识别最慢的操作：

```python
#!/usr/bin/env python3
"""识别性能瓶颈"""

import json
from pathlib import Path

def find_bottlenecks(trace_file: Path, top_n: int = 10):
    """识别最慢的工具调用"""
    with open(trace_file) as f:
        trace = json.load(f)
    
    tool_results = [
        event for event in trace["events"]
        if event["event_type"] == "tool_result" and event.get("tool_duration")
    ]
    
    # 按持续时间排序
    sorted_tools = sorted(
        tool_results,
        key=lambda x: x["tool_duration"],
        reverse=True
    )[:top_n]
    
    print(f"🐌 Top {top_n} slowest tool calls:\n")
    
    for i, tool in enumerate(sorted_tools, 1):
        duration = tool["tool_duration"]
        tool_name = tool["tool_name"]
        step = tool["step_name"]
        
        print(f"{i}. {tool_name} - {duration:.2f}s")
        print(f"   Step: {step}")
        print()

# 使用
trace_file = Path("logs/time-calendar/google-calendar/trace_summary_google-calendar.json")
find_bottlenecks(trace_file)
```

输出：

```
🐌 Top 10 slowest tool calls:

1. run_python - 8.45s
   Step: database_sampling_cycle_1

2. run_python - 7.23s
   Step: integration_tests

3. write_text - 2.15s
   Step: server_generation_cycle_1

4. read_text - 1.87s
   Step: code_review_cycle_1

5. write_text - 1.64s
   Step: database_generation_cycle_1
...
```

## 总结

这些示例展示了如何：

✅ 使用实时进度可视化  
✅ 分析追踪数据找出性能瓶颈  
✅ 监控工具调用行为  
✅ 追踪决策点和验证结果  
✅ 定制化分析工作流执行  

所有追踪数据都是结构化的 JSON 格式，易于编程处理和分析！

