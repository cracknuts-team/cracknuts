# 开发说明

## 项目目录说明

`src/` — 源码目录，用于存放项目正式代码  
`tests/` — 测试代码目录，用于存放单元测试及集成测试代码

## 分支说明

- `main` — 主分支，经过测试和评审的代码才能合并到此分支，保持最新稳定代码
- `major.minor_dev` — 特性开发分支，用于特定版本新特性开发阶段，功能稳定后合并到对应的 `major.minor` 分支
- `major.minor` — 版本稳定分支，存储该版本的稳定代码，后续只接受 bug 修复

开发人员应在本地分支完成功能开发及测试后，通过 Pull Request 向 `main` 或对应的 `major.minor` 分支提交合并请求。

## 开发环境

本项目使用 [uv](https://github.com/astral-sh/uv) 管理虚拟环境和依赖。

**1. 克隆仓库**

```shell
git clone https://github.com/cracknuts-team/cracknuts.git
cd cracknuts
```

**2. 安装 uv**（若已安装可跳过）

Linux / macOS：

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**3. 安装项目依赖**

```shell
uv sync
```

该命令会自动创建 `.venv/` 并以可编辑模式安装所有依赖（含开发依赖）。

**4. 安装 JavaScript 依赖**

```shell
cd jupyter_frontend
pnpm install
```

**5. 启动开发模式**

```shell
pnpm run dev
```

启用 HMR（热模块替换）需设置环境变量 `ANYWIDGET_HMR=1`：

```shell
# bash
ANYWIDGET_HMR=1 jupyter lab
```

```powershell
# PowerShell
$env:ANYWIDGET_HMR=1; jupyter lab
```

## 常用命令

| 任务 | 命令 |
|---|---|
| 运行 Python | `uv run python` |
| 运行脚本 | `uv run python <script.py>` |
| 运行测试 | `uv run pytest` |
| 添加依赖 | `uv add <package>` |
| 构建包 | `uv build` |

## 代码规范

- 变量、方法命名采用蛇形命名法（`snake_case`），类采用大驼峰（`PascalCase`）
- 方法参数和变量需声明类型注解
- 类中的日志 logger 必须使用完整包路径作为名称（例如 `cracknuts.cracker.cracker_s1`）
- Docstring 采用 reStructuredText（reST）格式

## 提交注释规范

所有提交信息必须使用**英文**编写。

**格式：**

```
<类型>[(<范围>)]: <简短描述>

[正文]

[尾部]
```

**类型说明：**

| 类型 | 适用场景 |
|---|---|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 仅修改文档 |
| `style` | 代码格式调整（不影响逻辑） |
| `refactor` | 代码重构（不引入新功能或修复 bug） |
| `test` | 添加或更新测试 |
| `chore` | 构建工具、配置文件、依赖等杂项变更 |

**规则：**

- 标题行限制在 50 个字符以内，使用祈使句（如 "Add X"，而非 "Added X"）
- 范围（scope）可选，用于标明所涉及的模块（例如 `fix(cracker):`）
- 标题与正文之间留一个空行

**示例：**

```
feat(cracker): add voltage configuration interface

Added new interface for configuring voltage settings.
Closes #42
```

```
fix: correct ADC sampling rate calculation
```
