# 命令行参数参考

## 基本用法

```bash
python main.py [OPTIONS]
```

## 参数列表

### 必需参数

虽然所有参数都有默认值，但通常你需要指定 schema 文件：

#### `--schema`
- **类型**: Path
- **默认值**: `mcp_servers\Time & Calendar\cf_1629.google-calendar-mcp_google-calendar_labeled.json`
- **说明**: MCP schema JSON 文件的路径
- **示例**: 
  ```bash
  python main.py --schema "mcp_servers/Social_Media/twitter.json"
  ```

### 输出配置

#### `--output-dir`
- **类型**: Path
- **默认值**: `generated`
- **说明**: 生成的模块和离线数据库的存储目录
- **示例**:
  ```bash
  python main.py --output-dir "my_output"
  ```

#### `--transcripts-dir`
- **类型**: Path
- **默认值**: `transcripts`
- **说明**: Agent 记录和辅助信息的存储目录
- **示例**:
  ```bash
  python main.py --transcripts-dir "my_transcripts"
  ```

### 模型配置

#### `--model`
- **类型**: String
- **默认值**: `deepseek/deepseek-chat` (或环境变量 `WORKFLOW_MODEL`)
- **说明**: 用于所有 Agent 的 LLM 模型标识符
- **支持的模型**: 
  - `deepseek/deepseek-chat`
  - `openai/gpt-4`
  - `anthropic/claude-3-5-sonnet-20241022`
  - 其他 LiteLLM 支持的模型
- **示例**:
  ```bash
  python main.py --model "openai/gpt-4"
  ```

#### `--api-key`
- **类型**: String
- **默认值**: None (从环境变量获取)
- **说明**: LiteLLM API 密钥，会回退到环境变量 `DEEPSEEK_API_KEY` / `LITELLM_API_KEY` / `API_KEY`
- **示例**:
  ```bash
  python main.py --api-key "your-api-key-here"
  ```

#### `--config`
- **类型**: Path
- **默认值**: `workflow/config/default.yaml`
- **说明**: 工作流配置 YAML 文件路径
- **示例**:
  ```bash
  python main.py --config "my_config.yaml"
  ```

### 执行控制

#### `--max-turns`
- **类型**: Integer
- **默认值**: `24`
- **说明**: 允许工作流的最大 Agent 轮次
- **建议值**: 
  - 简单 schema: 15-20
  - 中等复杂度: 20-30
  - 复杂 schema: 30-50
- **示例**:
  ```bash
  python main.py --max-turns 30
  ```

### 可观测性配置 🆕

#### `--no-progress`
- **类型**: Flag
- **默认值**: False (进度可视化默认启用)
- **说明**: 禁用实时进度可视化，使用简单文本输出
- **适用场景**:
  - CI/CD 环境
  - 终端不支持 ANSI 颜色
  - 需要简洁日志输出
- **示例**:
  ```bash
  # 禁用进度可视化
  python main.py --no-progress
  
  # 默认启用（无需参数）
  python main.py
  ```

## 常用命令组合

### 1. 基本开发使用
```bash
python main.py \
  --schema "mcp_servers/Time & Calendar/google-calendar.json"
```

### 2. 生产环境（禁用可视化）
```bash
python main.py \
  --schema "path/to/schema.json" \
  --no-progress \
  --max-turns 30 \
  --output-dir "production_output"
```

### 3. 自定义配置
```bash
python main.py \
  --schema "path/to/schema.json" \
  --config "production_config.yaml" \
  --api-key "your-api-key"
```

### 4. 使用不同模型
```bash
python main.py \
  --schema "path/to/schema.json" \
  --model "openai/gpt-4" \
  --api-key "sk-..."
```

### 5. 调试模式（更多轮次）
```bash
python main.py \
  --schema "path/to/schema.json" \
  --max-turns 50 \
  --enable-progress
```

## 环境变量

以下环境变量会影响工作流行为：

### API 配置
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（优先级最高）
- `LITELLM_API_KEY`: LiteLLM API 密钥
- `API_KEY`: 通用 API 密钥（优先级最低）
- `DEEPSEEK_BASE_URL`: DeepSeek API 基础 URL
- `LITELLM_BASE_URL`: LiteLLM API 基础 URL
- `BASE_URL`: 通用 API 基础 URL

### 工作流配置
- `WORKFLOW_MODEL`: 默认使用的模型（可被 `--model` 覆盖）
- `WORKFLOW_MAX_TURNS`: 最大轮次（可被 `--max-turns` 覆盖）
- `WORKFLOW_PYTHON_TIMEOUT`: Python 执行超时（秒）
- `WORKFLOW_MAX_REVIEW_CYCLES`: 最大审查循环次数
- `WORKFLOW_LOG_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `WORKFLOW_CONSOLE_LOGS`: 是否输出控制台日志（true/false）

### 示例：使用环境变量
```bash
export DEEPSEEK_API_KEY="your-key"
export WORKFLOW_MODEL="deepseek/deepseek-chat"
export WORKFLOW_MAX_TURNS=30

python main.py --schema "path/to/schema.json"
```

## 获取帮助

查看所有可用参数：

```bash
python main.py --help
```

输出：
```
usage: main.py [-h] [--schema SCHEMA] [--output-dir OUTPUT_DIR]
               [--transcripts-dir TRANSCRIPTS_DIR] [--model MODEL]
               [--max-turns MAX_TURNS] [--prompt PROMPT]
               [--api-key API_KEY] [--config CONFIG]
               [--enable-progress] [--no-progress]

Run the MCP offline server generation workflow.

optional arguments:
  -h, --help            show this help message and exit
  --schema SCHEMA       Path to the MCP schema JSON file.
  --output-dir OUTPUT_DIR
                        Directory where generated modules and offline
                        databases will be stored.
  --transcripts-dir TRANSCRIPTS_DIR
                        Directory where agent transcripts can be written by
                        downstream tooling.
  --model MODEL         OpenAI model identifier for all agents.
  --max-turns MAX_TURNS
                        Maximum number of agent turns to allow for the
                        workflow.
  --prompt PROMPT       High-level goal shared across agents during the
                        workflow.
  --api-key API_KEY     Override API key passed to LiteLLM (falls back to
                        DEEPSEEK_API_KEY / API_KEY environments).
  --config CONFIG       Path to workflow configuration YAML file. If not
                        provided, uses default locations.
  --enable-progress     Enable real-time progress visualization with Rich UI
                        (default: True).
  --no-progress         Disable real-time progress visualization.
```

## 故障排除

### 问题：找不到 schema 文件
```bash
FileNotFoundError: Schema file not found: ...
```

**解决方案**：确保路径正确，使用绝对路径或相对于工作目录的路径：
```bash
python main.py --schema "$(pwd)/mcp_servers/domain/file.json"
```

### 问题：API 密钥未设置
```bash
ValueError: API key is required. Please set one of the following environment variables: ...
```

**解决方案**：设置环境变量或使用 `--api-key` 参数：
```bash
export DEEPSEEK_API_KEY="your-key"
# 或
python main.py --api-key "your-key" --schema "..."
```

### 问题：进度显示错乱
如果终端不支持 Rich UI：
```bash
python main.py --no-progress --schema "..."
```

### 问题：Agent 轮次不足
```bash
RuntimeError: Code review did not pass after multiple iterations...
```

**解决方案**：增加最大轮次：
```bash
python main.py --max-turns 40 --schema "..."
```

## 高级用法

### 批量处理多个 schema

创建脚本 `batch_process.sh`：

```bash
#!/bin/bash

SCHEMAS=(
  "mcp_servers/Time & Calendar/google-calendar.json"
  "mcp_servers/Social_Media/twitter.json"
  "mcp_servers/Travel_Maps/airbnb.json"
)

for schema in "${SCHEMAS[@]}"; do
  echo "Processing: $schema"
  python main.py \
    --schema "$schema" \
    --no-progress \
    --max-turns 30 \
    2>&1 | tee "logs/$(basename "$schema" .json).log"
done
```

### CI/CD 集成

```yaml
# .github/workflows/generate.yml
name: Generate MCP Servers

on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
      
      - name: Generate servers
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          python main.py \
            --schema "mcp_servers/schema.json" \
            --no-progress \
            --max-turns 30
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: generated-servers
          path: generated/
```

## 参考资料

- [主文档](../README.md)
- [可观测性功能](OBSERVABILITY.md)
- [使用示例](OBSERVABILITY_EXAMPLE.md)
- [配置文件说明](../workflow/config/default.yaml)

