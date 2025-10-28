# MCP Offline Server Generation Workflow

一个基于多智能体协作的 MCP (Model Context Protocol) 离线服务器自动生成系统，具备强大的可观测性和实时进度追踪功能。

## ✨ 核心特性

- 🤖 **多Agent协作**：6个专业化Agent协同工作
- 📊 **实时进度可视化**：漂亮的终端UI实时显示执行状态
- 🔍 **完整可观测性**：详细追踪每个决策和工具调用
- 🎯 **智能审查循环**：自动迭代优化直到通过审查
- 📝 **结构化追踪**：JSONL格式实时记录，JSON格式完整摘要
- ⚙️ **高度可配置**：YAML配置文件支持灵活定制

## 🚀 快速开始

### 安装依赖

```bash
# 使用 uv (推荐)
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 运行工作流

```bash
# 基本用法（默认启用进度可视化）
python main.py --schema "mcp_servers/Time & Calendar/google-calendar.json"

# 禁用进度可视化
python main.py --schema "mcp_servers/Social_Media/twitter.json" --no-progress

# 使用自定义配置文件
python main.py \
  --schema "mcp_servers/Travel_Maps/airbnb.json" \
  --config "my_workflow_config.yaml"

# 完整示例：指定模型、输出目录
python main.py \
  --schema "mcp_servers/Travel_Maps/airbnb.json" \
  --model "deepseek/deepseek-chat" \
  --output-dir "my_output" \
  --max-turns 30
```

## 📁 项目结构

```
env-gen/
├── main.py                      # 命令行入口
├── workflow/                    # 核心工作流模块
│   ├── agents.py               # 6个专业化Agent定义
│   ├── context.py              # 工作流上下文和共享状态
│   ├── orchestrator.py         # 核心编排逻辑
│   ├── runtime.py              # 运行时初始化和执行
│   ├── observability.py        # 可观测性追踪系统 🆕
│   ├── progress.py             # 实时进度可视化 🆕
│   ├── tools.py                # Agent工具函数
│   ├── config.py               # 配置管理
│   ├── logging_utils.py        # 日志系统
│   └── config/                 # 配置文件
│       ├── default.yaml        # 默认配置
│       └── prompts.yaml        # Agent提示词
├── generated/                   # 生成的服务器代码和数据
├── logs/                        # 执行日志和追踪文件 🆕
├── tests/                       # 自动生成的测试
├── transcripts/                 # 执行记录
└── docs/                        # 文档 🆕
    ├── OBSERVABILITY.md         # 可观测性文档
    └── OBSERVABILITY_EXAMPLE.md # 使用示例
```

## 🔄 Workflow 流程

### 六个专业化 Agent

| Agent | 职责 |
|-------|------|
| 📋 **Schema Planner** | 分析schema，制定计划，记录DATA CONTRACT |
| 🗄️ **Database Synthesizer** | 生成离线数据库Python脚本 |
| ▶️ **Database Executor** | 执行数据库生成脚本，验证输出 |
| ⚙️ **Server Builder** | 实现FastMCP服务器和元数据 |
| 👀 **Code Reviewer** | 审查代码质量和一致性 |
| 🧪 **Test Agent** | 编写和执行自动化测试 |

### 执行阶段

1. **上下文准备**：解析schema、确定输出路径、收集预期工具名
2. **规划阶段**：Schema Planner分析并记录DATA CONTRACT
3. **数据库生成循环**（最多3轮）：
   - Database Synthesizer生成数据库脚本
   - Database Executor执行并验证
   - Server Builder实现服务器和元数据
   - Code Reviewer审查并提供反馈
4. **测试阶段**：Test Agent编写并运行pytest
5. **总结输出**：生成完整摘要和追踪文件

## 📊 实时进度可视化 🆕

运行时会看到漂亮的实时进度界面：

```
╭────────────────────────────────────────────────────────────╮
│ 🚀 MCP Workflow Execution  |  Elapsed: 2m 34s              │
╰────────────────────────────────────────────────────────────╯

╭─ Workflow Stages ──────────────────────────────────────────╮
│ Stage                     Status        Duration  Turns    │
│ 📋 Schema Planning        ✅ completed  15s       4        │
│ 🗄️ Database Generation   ✅ completed  45s       8        │
│ ▶️ Database Execution     ✅ completed  8s        2        │
│ ⚙️ Server Implementation   ▶️ in_progress 23s      6        │
│ 👀 Code Review            ⏳ pending     -        -        │
│ 🧪 Integration Testing    ⏳ pending     -        -        │
╰────────────────────────────────────────────────────────────╯

╭─ Recent Tool Calls ────────────────────────────────────────╮
│ 🔧 Tool Activity                                            │
│ ├── 14:32:15 [Server Builder] → write_text                │
│ ├── 14:32:12 [Server Builder] → read_text                 │
│ └── 14:32:10 [Database Executor] → run_python             │
╰────────────────────────────────────────────────────────────╯
```

## 🔍 可观测性追踪 🆕

### 自动生成的追踪文件

- **实时追踪**：`logs/{domain}/{slug}/trace_YYYYMMDD_HHMMSS.jsonl`
- **完整摘要**：`logs/{domain}/{slug}/trace_summary_{slug}.json`

### 追踪的事件类型

- Agent 开始/结束/轮次
- 工具调用及结果（含参数和耗时）
- 决策点（审查判决、数据库更新决策等）
- 验证检查（DATA CONTRACT、元数据工具等）
- 错误事件
- 自定义注释

### 使用示例

```python
import json

# 读取完整摘要
with open("logs/domain/slug/trace_summary_slug.json") as f:
    trace = json.load(f)
    
    # 分析性能
    for step, data in trace["summary"]["traces"].items():
        print(f"{step}: {data['formatted_duration']}")
    
    # 工具使用统计
    for agent, count in trace["summary"]["tool_calls_by_agent"].items():
        print(f"{agent}: {count} tool calls")
```

详见：[可观测性文档](docs/OBSERVABILITY.md) | [使用示例](docs/OBSERVABILITY_EXAMPLE.md)

## ⚙️ 配置

通过 `workflow/config/default.yaml` 配置工作流行为：

```yaml
execution:
  max_turns_per_agent: 20
  python_timeout_seconds: 180.0

review:
  max_review_cycles: 3

validation:
  require_data_contract: true
  strict_sample_validation: true

model:
  default_model: deepseek/deepseek-chat
  default_base_url: https://api.deepseek.com
```

Agent提示词可在 `workflow/config/prompts.yaml` 中自定义。

## 📝 输出文件

成功执行后会生成：

- `generated/{domain}/{slug}/{slug}_server.py` - FastMCP服务器实现
- `generated/{domain}/{slug}/{slug}_database.py` - 数据库生成脚本
- `generated/{domain}/{slug}/{slug}_database.json` - 离线数据库JSON
- `generated/{domain}/{slug}/{slug}_metadata.json` - 工具元数据
- `tests/{domain}/{slug}/` - 自动化测试
- `logs/{domain}/{slug}/` - 日志和追踪文件 🆕

## 🛠️ 开发

### 运行测试

```bash
pytest tests/
```

### 检查代码

```bash
# 类型检查
mypy workflow/

# 代码格式化
black workflow/
```

## 📚 更多文档

- [命令行参数参考](docs/CLI_REFERENCE.md) - 完整的命令行参数说明
- [可观测性功能详解](docs/OBSERVABILITY.md) - 实时进度追踪和事件记录
- [可观测性使用示例](docs/OBSERVABILITY_EXAMPLE.md) - 实用的分析脚本示例

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License
