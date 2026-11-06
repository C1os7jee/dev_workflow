# Dev Workflow

将 Matt Pocock 的 12 个原版工程 skills 集成为一个开发入口，按需求大小编排完整流程。

用户只需调用 `$dev-workflow`。技能执行各阶段时读取仓库内对应的原版正文、模板和参考资料，无需另外安装或手工切换这些技能。

## 安装

以下以 Codex 为例，任选一种方式安装即可。仓库根目录就是完整技能包，入口为 [SKILL.md](SKILL.md)，请保留全部配套文件；无需另外安装内置的 12 个原版技能。

### 方式一：让 Codex 安装

将下面这段话发送给 Codex：

```text
$skill-installer
请从 https://github.com/C1os7jee/dev_workflow 的仓库根目录安装技能，
名称使用 dev-workflow，并保留全部配套文件。
```

Codex 会使用内置安装器处理 GitHub 仓库中的技能。安装完成后，如果技能列表中还没有出现 `dev-workflow`，重启 Codex。

### 方式二：使用终端命令

需要 Node.js 22.20 或更高版本。在终端执行：

```bash
npx skills@latest add C1os7jee/dev_workflow --skill dev-workflow -a codex -g --copy
```

| 参数 | 含义 |
| --- | --- |
| `--skill dev-workflow` | 选择本仓库的统一技能入口 |
| `-a codex` | 安装给 Codex |
| `-g` | 安装到个人目录，供不同项目使用 |
| `--copy` | 复制文件，避免依赖符号链接 |

如果只想给当前项目安装，请先进入项目目录，执行不带 `-g` 的命令：

```bash
npx skills@latest add C1os7jee/dev_workflow --skill dev-workflow -a codex --copy
```

安装前也可以只列出仓库中的可用技能：

```bash
npx skills@latest add C1os7jee/dev_workflow --list
```

本仓库只提供一个安装入口：`dev-workflow`。

## 使用

在 Codex 中打开实际要开发的项目目录，输入 `$dev-workflow` 并描述目标。创建新项目时，打开准备存放项目的目录即可。

### 小需求或 Bug 修复

```text
$dev-workflow
修复运费计算：订单金额恰好达到免运费门槛时，仍然收取运费。
请检查现有规则，修复并完成相关验证。
```

目标和验收明确时，技能会检查项目并直接推进实现或诊断、验证和审查；遇到影响业务规则的歧义时再提问。

### 大需求或新项目

```text
$dev-workflow
我想开发一个团队设备预约系统，支持查看设备、预约、取消和管理员维护。
先帮我梳理首版范围、业务规则和验收标准，再形成方案并开发。
```

技能先澄清需求，请你确认范围和验收；再展示方案、任务与验证策略，请你确认后实施。项目准备已内置，无需单独运行 setup，也不用手工切换内置技能。

### 继续上次的任务

```text
$dev-workflow
继续设备预约系统的开发，先读取已有工作记录，
沿用已经确认的需求和方案，从上次未完成的阶段继续。
```

大需求默认集中维护一份本地工作记录，优先沿用项目现有位置；没有约定时使用 `.scratch/<需求名>/work.md`。新会话中可提供该文件路径，方便恢复进度。

- 小需求：项目检查 → 明确目标与验收 → 实现或诊断 → 验证与审查 → 交付。
- 大需求：项目检查 → 需求澄清与确认 → 设计、规格及任务拆分 → 方案确认 → 实施 → 验证与审查 → 交付。

大小由影响范围、不确定性、复杂度和风险判断，用户可以纠正。主 Agent 按实际收益组织子 Agent 并负责集成验收；已有项目约定、用户修改和授权边界继续有效。

## 更新

使用上述 `skills` 命令安装的用户，可按安装范围更新：

```bash
# 更新个人目录中安装的 dev-workflow
npx skills@latest update dev-workflow -g

# 在项目目录中更新该项目安装的 dev-workflow
npx skills@latest update dev-workflow -p
```

这些命令只更新由 `skills` 安装工具管理的副本。通过 `$skill-installer` 安装的用户，可让 Codex 检查并更新来自本仓库的安装。更新后如果仍未识别到新内容，重启 Codex。

安装与调用方式参考 [OpenAI 技能文档](https://developers.openai.com/codex/skills/)；终端工具的环境要求参考 [skills README](https://github.com/vercel-labs/skills#install-a-skill)，安装和更新参数参考 [skills CLI 文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

## 内置原版技能

| 阶段 | 内置模块 |
| --- | --- |
| 项目准备 | `setup-matt-pocock-skills` |
| 需求与设计 | `grill-with-docs`、`grilling`、`domain-modeling`、`codebase-design` |
| 规格与任务 | `to-spec`、`to-tickets` |
| 实施 | `implement`、`implement-spec`、`tdd` |
| 诊断与审查 | `diagnosing-bugs`、`code-review` |

原版正文及配套文件放在 `references/matt-pocock/`。12 个原版 `SKILL.md` 改名为内部的 `instructions.md`，根目录保留唯一的 `SKILL.md` 入口。36 个上游文件中，34 个内容逐字节保留，另外两个仅调整三处返回入口的 Markdown 链接。

- [小需求编排](references/small.md)
- [大需求编排](references/large.md)
- [内部调用映射与必要适配](references/integration.md)
- [逐文件来源、哈希与变换清单](references/matt-pocock/sources.json)

单份工作记录、确认关口合并及操作授权等适配集中在集成说明中，原版工程正文未被摘要重写。

## 来源与校验

上游为 [mattpocock/skills](https://github.com/mattpocock/skills)，固定提交：

```text
4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
```

运行离线包校验，只需 Python 标准库：

```bash
python scripts/verify_bundle.py
```

如有本地上游 Git 仓库，可进一步对照固定提交的全部原始文件：

```bash
python scripts/verify_bundle.py --upstream /path/to/mattpocock-skills
```

校验器不会访问网络或修改文件。技能运行时不自动下载、更新上游内容。

## 验证范围

已完成来源重建校验、独立审查、小功能与 bug 修复演练，以及大需求两个确认关口和跨上下文恢复演练。未将完整大项目的并行实施、远程任务跟踪器或真实部署视为已通过端到端验证。

## 许可

MIT。保留 Matt Pocock 原版技能的版权与许可，详见 [LICENSE](LICENSE)。
