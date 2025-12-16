# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是 Deep Agents 项目的学习仓库,包含三个主要 Python 包:

1. **deepagents** - 核心代理框架,基于 LangGraph 构建
2. **deepagents-cli** - 命令行界面,类似 Claude Code 的终端代理
3. **harbor** - 使用 Harbor 和 LangSmith 进行代理评估的框架

## 项目结构

```
libs/
├── deepagents/          # 核心框架
│   ├── deepagents/
│   │   ├── graph.py            # create_deep_agent() 主入口
│   │   ├── middleware/         # 中间件系统
│   │   │   ├── filesystem.py   # 文件系统工具
│   │   │   ├── subagents.py    # 子代理委派
│   │   │   └── patch_tool_calls.py
│   │   └── backends/           # 存储后端
│   │       ├── state.py        # 临时内存存储
│   │       ├── filesystem.py   # 本地文件系统
│   │       ├── store.py        # 持久化存储
│   │       ├── composite.py    # 组合后端
│   │       └── sandbox.py      # 沙箱执行
│   └── tests/
├── deepagents-cli/      # CLI 应用
│   └── deepagents_cli/
│       ├── agent.py            # CLI 代理配置
│       ├── agent_memory.py     # 记忆系统
│       ├── main.py             # CLI 入口
│       ├── execution.py        # 执行循环
│       ├── tools.py            # CLI 特定工具
│       ├── ui.py               # 用户界面
│       ├── input.py            # 输入处理
│       ├── shell.py            # Shell 执行
│       ├── skills/             # 技能系统
│       └── integrations/       # 沙箱集成
└── harbor/              # 评估框架
    ├── deepagents_harbor/
    │   ├── deepagents_wrapper.py  # Harbor 适配器
    │   ├── backend.py             # 沙箱后端
    │   └── tracing.py             # LangSmith 追踪
    └── scripts/
        ├── harbor_langsmith.py    # LangSmith 集成
        └── analyze.py             # 结果分析
```

## 常用命令

### 环境设置

```bash
# 安装依赖(使用 uv,推荐)
uv sync --all-groups

# 或使用 pip
pip install -e libs/deepagents
pip install -e libs/deepagents-cli
```

### deepagents - 核心框架

```bash
cd libs/deepagents

# 运行单元测试
make test
# 或指定测试文件:
uv run pytest tests/unit_tests --cov=deepagents --cov-report=term-missing

# 运行集成测试
make integration_test

# 代码格式化
make format

# 代码检查(ruff + mypy)
make lint
```

### deepagents-cli - 命令行工具

```bash
cd libs/deepagents-cli

# 运行 CLI(开发模式)
uv run deepagents

# 或安装后运行
uv pip install -e .
deepagents

# 运行测试
make test

# 运行集成测试
make test_integration

# 代码格式化和检查
make format
make lint
```

### harbor - 评估框架

```bash
cd libs/harbor

# 配置环境变量
export ANTHROPIC_API_KEY="sk-ant-..."
export LANGSMITH_API_KEY="lsv2_..."
export LANGSMITH_TRACING_V2=true

# 运行 Terminal Bench 评估(Docker,1个任务)
make run-terminal-bench-docker

# 运行 Terminal Bench 评估(Daytona,10个任务)
make run-terminal-bench-daytona

# 运行 Terminal Bench 评估(Modal,4个任务)
make run-terminal-bench-modal

# 或直接使用 harbor 命令
harbor run --agent-import-path deepagents_harbor:DeepAgentsWrapper \
  --dataset terminal-bench@2.0 -n 1 --jobs-dir jobs/terminal-bench --env docker

# 运行测试
make test
```

## 架构要点

### 1. Deep Agent 核心模式

`create_deep_agent()` 是主要入口点,实现了经过验证的代理设计模式:

- **中间件系统**: 使用可组合的中间件注入工具和功能
  - `TodoListMiddleware` - 任务规划和进度跟踪
  - `FilesystemMiddleware` - 文件操作 (ls, read_file, write_file, edit_file, glob, grep, execute)
  - `SubAgentMiddleware` - 子代理委派和并行执行
  - `SummarizationMiddleware` - 上下文超过 170k tokens 时自动摘要
  - `AnthropicPromptCachingMiddleware` - 缓存系统提示以降低成本
  - `HumanInTheLoopMiddleware` - 人机交互审批

- **存储后端**: 可插拔的后端控制文件系统操作
  - `StateBackend` (默认) - 临时状态中的文件
  - `FilesystemBackend` - 真实磁盘操作
  - `StoreBackend` - 使用 LangGraph Store 的持久化存储
  - `CompositeBackend` - 将不同路径路由到不同后端

### 2. CLI 架构 (deepagents-cli)

- **记忆系统**: 双层记忆架构
  - 全局 `~/.deepagents/<agent_name>/agent.md` - 个性化和通用偏好
  - 项目级 `.deepagents/agent.md` - 项目特定上下文
  - 额外的项目记忆文件 - 按需加载的结构化知识

- **技能系统**: 渐进式披露模式
  - 技能在 `~/.deepagents/<agent_name>/skills/` 或 `.deepagents/skills/`
  - 启动时加载元数据(name + description)
  - 仅在需要时读取完整的 SKILL.md 内容
  - 示例技能: web-research, langgraph-docs

- **项目感知**: 自动检测项目根目录(通过 `.git`)并加载项目配置

### 3. Harbor 评估框架

- **沙箱环境**: 支持多种后端(Docker, Modal, Daytona, Runloop)
- **自动测试**: 运行测试并验证结果
- **奖励评分**: 基于测试通过率的 0.0-1.0 分数
- **轨迹记录**: ATIF 格式(Agent Trajectory Interchange Format)
- **LangSmith 集成**: 追踪、分析和迭代改进

### 4. 中间件提示注入

中间件会自动注入工具说明到系统提示中。编写自定义 `system_prompt` 时:

- ✅ 定义领域特定的工作流程
- ✅ 提供具体示例
- ✅ 添加专业指导
- ✅ 定义停止条件和资源限制
- ❌ 不要重新解释标准工具(中间件已覆盖)
- ❌ 不要与默认说明冲突

## 依赖关系

### 核心依赖
- langchain >= 1.1.0
- langchain-core >= 1.1.0
- langchain-anthropic >= 1.2.0
- wcmatch (用于 glob 模式匹配)

### 测试依赖
- pytest
- pytest-cov
- pytest-xdist
- pytest-asyncio
- ruff (代码检查和格式化)
- mypy (类型检查)

### CLI 额外依赖
- rich (终端 UI)
- prompt_toolkit (输入处理)

### Harbor 额外依赖
- harbor-ai (评估框架)
- langsmith (追踪和分析)

## 代码风格

### Ruff 配置
- 行长度: 150
- 使用 Google 风格的文档字符串
- 启用所有规则,但忽略与格式化冲突的规则
- 在文档字符串中格式化代码块

### MyPy 配置
- 严格模式启用
- 忽略缺失的导入
- 启用弃用错误代码

### 测试
- 单元测试: `tests/unit_tests/`
- 集成测试: `tests/integration_tests/`
- 使用 pytest 的 asyncio 模式

## LangSmith 评估工作流

```bash
# 1. 创建数据集
python scripts/harbor_langsmith.py create-dataset terminal-bench --version 2.0

# 2. 创建实验
python scripts/harbor_langsmith.py create-experiment terminal-bench --name deepagents-baseline-v1

# 3. 运行带追踪的基准测试
export LANGSMITH_EXPERIMENT="deepagents-baseline-v1"
make run-terminal-bench-daytona

# 4. 添加反馈分数
python scripts/harbor_langsmith.py add-feedback jobs/terminal-bench/<timestamp> \
  --project-name deepagents-baseline-v1
```

## 关键文件位置

- 主入口点: `libs/deepagents/deepagents/graph.py:create_deep_agent()`
- CLI 入口: `libs/deepagents-cli/deepagents_cli/main.py`
- Harbor 适配器: `libs/harbor/deepagents_harbor/deepagents_wrapper.py`
- 中间件定义: `libs/deepagents/deepagents/middleware/`
- 后端实现: `libs/deepagents/deepagents/backends/`

## 重要概念

### SubAgents (子代理)
- 用于上下文隔离和并行执行
- 通过 `task` 工具从主代理调用
- 可以有自定义指令、工具和模型
- 可以传递预构建的 LangGraph 图

### Backends (后端)
- 控制文件系统操作的位置和方式
- 支持临时、持久化和混合存储
- `execute` 工具仅在实现 `SandboxBackendProtocol` 的后端上可用

### 长期记忆
- 使用 `CompositeBackend` 将特定路径路由到持久化存储
- 示例: `/memories/` 跨会话持久化,其他路径保持临时
- 用例: 用户偏好、知识库、自我改进指令

## 默认模型

- 默认: `claude-sonnet-4-5-20250929`
- 最大 tokens: 20000
- 可通过 `model` 参数自定义为任何 LangChain 模型
