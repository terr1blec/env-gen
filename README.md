# Tool Environment Generation

## 项目结构
- `main.py`：命令行入口，解析参数后启动完整的离线生成工作流。
- `workflow/context.py`：定义 `WorkflowContext`，负责解析 schema、管理路径、记录 DATA CONTRACT 等共享状态。
- `workflow/runtime.py`：构建上下文、初始化日志与模型，并包装 `execute_workflow` 的运行与错误输出。
- `workflow/orchestrator.py`：实现核心编排逻辑，依次驱动规划、数据集生成、服务器实现、代码审查、数据集执行与测试阶段，并内置数据契约和工具覆盖校验。
- `workflow/agents.py`：声明各个代理角色及指令，限制其可用工具与职责范围。
- `workflow/tools.py`：提供文件读写、目录管理、运行 Python 等通用工具，并确保所有写入落在允许目录内。
- `generated/`：存放离线生成的服务器代码、数据集与元数据（按域/slug 分类）。
- `logs/`：记录工作流执行日志，便于回溯各阶段输出与错误。
- `tests/`：生成或手写的测试文件目录，验证服务器实现与离线数据。
- `transcripts/`：供代理或辅助脚本输出补充说明、运行记录的目录。

## Workflow 流程概述
1. **上下文准备**：`prepare_context` 解析 schema、确定输出路径、收集预期工具名，并生成 DATA CONTRACT 摘要。
2. **规划阶段**：Schema Planner 读取 schema 与上下文信息，记录 DATA CONTRACT、实现要点及待办笔记。
3. **迭代生成**：
   - Dataset Synthesizer 根据 DATA CONTRACT 生成离线数据与脚本。
   - Server Builder 实现 FastMCP 服务器和 metadata JSON，并与离线数据保持一致。
   - Code Reviewer 检查实现是否满足契约与工具覆盖，必要时反馈修改；最多进行三轮。
4. **数据集执行**：Dataset Executor 运行生成脚本，确认 JSON 结构符合 DATA CONTRACT。
5. **集成测试**：Test Agent 在 `tests/` 目录编写并运行测试，验证服务器能加载离线数据、工具接口与 metadata 对齐。
6. **总结输出**：`run_workflow` 汇总各阶段结果至日志与终端，必要时报告终止原因。
