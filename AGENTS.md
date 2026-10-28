# 项目协作约定

## 规则体系（必须遵守）

`docs/07-规则文档/` 是本项目的规则来源。**该目录仅保存在本地，已在 `.gitignore` 排除，不提交、不推送**（含明文凭据）。规则分两类使用：

### 一、常驻规则：全程生效，不得遗漏

**`docs/07-规则文档/项目整体规则.md`** —— 每次开始工作前先读取并全程遵守，内容涵盖：

- 中文回复；macOS ARM64 指令规范
- Java 17（非 JDK 8）、Maven 固定目录与 `settings.xml`、本地仓库路径
- Python 依赖只用 `uv`（禁用 pip）；前端只用 `pnpm`（禁用 npm）
- 开发库 MySQL / Redis 地址与 MCP 使用方式
- 远程服务器与组件安装约定

> 该文件是项目硬约束，**任何任务都适用**。若与本文件其他条款冲突，以 `项目整体规则.md` 为准。

### 二、场景规则：按需智能加载

命中下列场景时，先读对应规则文件再动手：

| 场景 | 规则文件 |
| --- | --- |
| 启动 / 调试后端 `yudao-server` 或前端 `yudao-ui-admin-vue3`、打包、看日志判就绪、curl 调接口 | `前后端项目启动规则.md` |
| 部署到远程测试机 `10.206.65.236` / `10.206.67.2`、安装对象存储等新组件、远程运维 | `前后端远程测试环境部署规则.md` |
| 编写或修改 Java 代码、新增后端模块、设计类与方法 | `工程设计规范.md` |

### 三、执行要求

1. 任务开始前先判断属于哪类场景，命中则读取对应规则文件；**不要凭记忆猜测规则内容**。
2. 常驻规则全程有效，即使任务看起来不涉及（例如写文档也需中文、调用命令也需遵守环境约束）。
3. 规则文件已变更时以文件当前内容为准；若发现规则与工程实际不符，**先指出差异再确认**，不擅自修改。
4. 本目录含凭据，**禁止提交、推送到任何远程仓库，禁止外传**。

---

## 语言

- 面向用户的回复、阶段提交、确认问题和项目文档默认使用简体中文。
- 代码标识、协议名、框架名、命令、API 字段和行业固定术语保留通用写法。
- 用户明确指定其他语言时，以该次要求为准。

## 目录命名

- `docs/` 下每一级目录使用两位连续编号与中文语义名称，顶层从 `00` 起、子目录从 `01` 起，并优先复用已有阶段目录。
- 架构文档统一归档到 `docs/03-架构/`。
- 文档类子目录优先使用 `文档`、`资料`、`图表`、`评审`、`决策`、`资产`、`演示` 等语义名称，并按所在层级编号。
- `frontend/`、`backend/`、源码目录、构建工具约定目录及技术生态固定名称保持原名。
- 调整历史目录前先检查链接、脚本、清单和固定包影响；批量迁移须取得用户明确授权。

## 阶段与资产保护

- 新增文件前先复用现有目录，保持单一归档位置。
- 文档按设计或实现对象维护一个当前版本，优先更新原文件；保留当前规格、设计源文件、必要依据及验证工具。
- 已被替代的草稿、旧版 Demo、重复确认表单和临时检查回执及时清理；实际确认结论集中在 `docs/03-架构/01-决策/当前有效决策.md`，阅读入口为 `docs/README.md`。
- 清理前核对引用与实际确认依据；仅改变文档组织不会重新批准业务方案。修改已确认的需求、设计或技术方案仍须用户确认。
- 后端本地运行配置 `backend/yudao-boot-mini/yudao-server/src/main/resources/application-local.yaml` 保持不读不改。

<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->
