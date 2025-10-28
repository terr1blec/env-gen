# Workflow Configuration

## 文件说明

### `default.yaml`
主配置文件，包含：
- `execution`: 执行参数（超时、最大轮数等）
- `review`: 审查流程配置
- `directories`: 目录结构
- `file_naming`: 文件命名规则
- `logging`: 日志配置
- `model`: LLM 模型配置
- `validation`: 验证规则

### `prompts.yaml`
Agent 提示词配置，包含 6 个 agent 的 instructions：
- `schema_planner`: Schema 规划 agent
- `dataset_builder`: 数据库生成 agent
- `server_builder`: 服务器构建 agent
- `reviewer`: 代码审查 agent
- `dataset_executor`: 数据库执行 agent
- `test_agent`: 测试 agent

## 使用方式

### 1. 使用默认配置
```python
from workflow import run_workflow
await run_workflow(args)  # 自动加载 workflow/config/default.yaml
```

### 2. 自定义配置
在项目根目录创建 `config.yaml`:
```yaml
review:
  max_review_cycles: 5  # 修改审查次数

logging:
  level: DEBUG  # 修改日志级别
```

然后运行：
```bash
python main.py --schema path/to/schema.json
```

### 3. 修改 Agent Prompts
直接编辑 `prompts.yaml` 文件：
```yaml
schema_planner: |
  你是一个 Schema 规划专家...
  （修改这里的提示词）

dataset_builder: |
  你负责生成数据库...
  （修改这里的提示词）
```

### 4. 环境变量覆盖
```bash
export WORKFLOW_MAX_REVIEW_CYCLES=10
export WORKFLOW_LOG_LEVEL=DEBUG
python main.py --schema path/to/schema.json
```

## 配置优先级

1. 命令行参数指定的配置文件
2. 项目根目录的 `config.yaml`
3. `workflow/config/default.yaml` （默认）

Agent prompts 自动从配置文件同目录的 `prompts.yaml` 加载。

