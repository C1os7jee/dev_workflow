# 集成约定与原版调用映射

本包保存指定上游提交的原版资料。只在下列列明的宿主调用、阶段确认、文档存储及授权衔接处适配；原文中其余方法、检查要求与模板照常执行。项目指令与用户已确认的契约优先，不能把原文中的操作当成新增授权。

## 模块加载

根目录 `SKILL.md` 是唯一入口。原文中“Call the Skill tool”、`/技能名` 或“让用户运行某技能”均在当前流程内解析到下表：读取对应文件，按其步骤执行，将产物返回当前阶段，不调用本机其他同名技能。

| 模块 | 包内正文 | 阶段与输入输出 |
| --- | --- | --- |
| setup-matt-pocock-skills | [instructions.md](matt-pocock/setup-matt-pocock-skills/instructions.md) | 开始时识别项目，提供 tracker、领域文档和适用标签约定 |
| grill-with-docs | [instructions.md](matt-pocock/grill-with-docs/instructions.md) | 需求访谈入口，内部加载以下两个模块 |
| grilling | [instructions.md](matt-pocock/grilling/instructions.md) | 按依赖分轮澄清，产出待确认目标与规则 |
| domain-modeling | [instructions.md](matt-pocock/domain-modeling/instructions.md) | 术语、场景和必要 ADR，配套格式留在本目录 |
| codebase-design | [instructions.md](matt-pocock/codebase-design/instructions.md) | 接口与模块设计，需要时加载其深化或多方案参考 |
| to-spec | [instructions.md](matt-pocock/to-spec/instructions.md) | 已有讨论 → 原版模板规格与测试决策 |
| to-tickets | [instructions.md](matt-pocock/to-tickets/instructions.md) | 规格 → 纵向任务、阻塞关系与验收 |
| implement | [instructions.md](matt-pocock/implement/instructions.md) | 已明确请求或任务 → 实现、验证与任务审查 |
| implement-spec | [instructions.md](matt-pocock/implement-spec/instructions.md) | 已确认任务图 → 调度、集成与整体审查 |
| tdd | [instructions.md](matt-pocock/tdd/instructions.md) | 已确定的公开测试边界 → 行为测试与最小实现 |
| diagnosing-bugs | [instructions.md](matt-pocock/diagnosing-bugs/instructions.md) | 实际症状 → 复现、诊断、修复与回归 |
| code-review | [instructions.md](matt-pocock/code-review/instructions.md) | 本次变更、规范与验收 → Standards / Spec 两项结论 |

配套资料的相对路径以对应模块目录为基准。原文 frontmatter 的调用策略及 `agents/openai.yaml` 作为上游资料保留，不参与本包的入口注册，也不阻止内部模块加载。只有表内模块可内部调用；原文提到但本包未包含的技能不能成为隐式依赖。

## 1. 项目准备：复用与按需配置

每次读取 setup 正文并做与项目相关的探索，提供其消费者需要的 tracker、领域文档与适用标签信息。已有项目约定足够就直接复用；缺少的仅为当前会话临时上下文、且不影响实施时先用上下文，不强制写初始化文件。

默认使用本地工作记录。已有项目明确采用其他跟踪方式时沿用；不因存在远程仓库就自动选择远程 tracker 或创建标签。远程接入、Git remote 和外部写操作只在用户实际要求且已授权时实施。

首次缺少且值得跨需求复用的约定，展示简短草案并集中确认后，补入已有文档；无合适文件时采用 `AGENTS.md`。已有适用的 `AGENTS.md` 或 `CLAUDE.md` 优先，不重复建另一套。保留正文中已确认术语与 ADR 的按需记录规则，不自动迁移旧文档名字。

只有本包实际执行 triage 工作时才需要 triage 标签；本包不包含 triage，不能因为全局恰好装了它，就触发其配置。消费者中的标签默认可作为本地任务状态词，不向远程创建标签。

## 2. 一份本地需求工作记录

大需求优先沿用项目已有需求文档；没有约定时使用 `.scratch/<需求名>/work.md`。保留以下内容并持续更新：

- 当前阶段、下一步、阻碍及已加载模块。只有原文已被实际读取执行才记录为已加载，不把阶段名称当作加载证据。
- 已确认目标、范围和验收，待决问题，需求确认与方案确认的简短依据。
- `to-spec` 原版模板的全部适用章节：Problem Statement、Solution、User Stories、Implementation Decisions、Testing Decisions、Out of Scope、Further Notes。规格中不放易失效的路径或实现细节；执行路径放任务章节。
- `to-tickets` 原版模板字段：每个任务独立的稳定编号、标题、Status、Blocked by、内容及验收。放在同一文档的独立章节，例如 `#ticket-01`，无需每个 ticket 一个文件。
- 任务执行者、结果、实际验证、审查发现及其处理状态，已完成与未验证分开记录。
- 任务起点：起始提交（若有）、原有工作区状态、相关初始差异；无 Git 保存实际涉及文件可比较的原始内容或快照位置，新文件记原先不存在。恢复时核对他人后续修改，避免覆盖或误归因。

“publish / fetch / close ticket”在默认本地模式分别是更新规格或任务章节、读取对应章节、记录结果并更新状态；“claim”先由主 Agent 在任务中登记执行者，避免重复派发。只有全部阻塞任务完成的未分配任务可以就绪执行。子 Agent 返回结果，由主 Agent 统一更新共享工作记录，避免并发写同一文件。

原版 local tracker 模板完整保留作为资料，不能原样复制其中的 `spec.md` 和 `issues/` 多文件规则来覆盖此处已确认的单文档规则。GLOSSARY / ADR 是项目知识，确有内容时按原版和项目约定记录，与单份需求工作记录不重复。

小需求默认用当前会话中的明确请求与验收作为规格来源，跟踪信息可以留在会话；不为了 `to-spec`、tracker 或审查的前提强制另建文档。

## 3. 确认和测试衔接

- 大需求的 `grilling` 收敛并确认需求后，进入设计；`to-spec` 的测试边界与 `to-tickets` 的任务提问集中到方案确认。用户明确接受已展示方案之后连续实施，不逐个重复批准测试。
- 小需求沿用当前请求和项目已明确的公开接口、行为及测试约定，先说明所用边界即可执行；遇到会改变业务规则或公开契约的歧义必须先确认。没有必要为了形式再进行完整访谈。
- TDD 的行为断言、测试入口、逐个失败与实现等方法保留。文案、样式、配置采用可证明效果的检查，不强制造单元测试；缺少可用测试入口时如实说明。原版 `implement` 的类型检查和全套测试，按项目实际存在的命令及相关风险选择，未运行项目明确要求的检查要标明未完成。
- 诊断保留原版反馈循环、最小复现和证伪方法。已经由诊断完成的修复与回归不再重新跑一遍实现；合理跳过阶段依原文明确说明依据。 原版要求写入 commit / PR message 的已验证根因和关键证据，在没有提交或 PR 授权时写入交付说明；大需求同时记入现有工作记录，日后获授权提交时再用于对应 message。

## 4. 多 Agent、版本控制与外部操作

`implement-spec` 的任务图、独立上下文、就绪任务调度和主 Agent 集成责任保留。有并行收益才分派，代码任务具有不相交写集；共享接口先确定，子 Agent读取本文件及实际需要的原文。

- 没有已获授权的提交或 PR 流程时，在现有工作区按互斥写集实施；主 Agent 整合实际文件，不执行原版自动提交、分支合并、关闭远程 issue 或发布 PR 的动作。需要隔离时可使用合适的 worktree，不为并行本身改动 Git 历史。
- 用户已授权的分支和提交流程才使用对应原版步骤；不得使用 reset 清除工作、覆盖他人修改或借初始化擅自调整远程配置。主 Agent 验收任务结果与完整集成结果。
- 大需求审查使用原版独立 Standards / Spec 审查者，只读；小需求由主 Agent 按相同两轴方法检查。审查报告保持两项结论分开，不跨轴稀释问题。
- 项目明确采用当前新契约时，原版 `to-tickets` 对 wide refactor 的 expand–contract 不能自动引入兼容层。先检查真实调用方和数据迁移要求；兼容或不可逆迁移属于需明确决定的方案，不凭模板默认增加。
- 上游诊断的 HITL 脚本为 Bash，原文件照存；只有实际需要且运行环境支持才使用。不把 Bash 文本当 PowerShell 执行，不以不同语义的备用操作掩盖不可用环境。

## 5. 审查范围和重复阶段

任务起点、当前工作区及任务产物共同确定本次审查范围，覆盖已提交、暂存、未暂存和新增文件，区分用户原有修改；向 `code-review` 提供明确比较命令或初始文件对比。没有提交或 Git 时直接审查文件，不能以三点 diff 为空判断没有修改，也不要求先提交。验收来源可以是明确用户请求或工作记录规格，避免再次要求用户寻找已经存在的信息。

`implement` 内触发的任务审查、`implement-spec` 收尾的集成审查与外层收尾衔接为一次对应范围的检查。记录已完成的范围和结果；集成新增变更或整改后仅补充必要重查。发现问题后修改代码，再执行受影响验证，未通过验收不能关闭任务。

## 来源与差异记录

来源固定为 `mattpocock/skills` 提交 `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`。文件清单与逐项源哈希、包内哈希及变换见 [sources.json](matt-pocock/sources.json)。共 12 个模块、36 个上游文件。

12 个上游 `SKILL.md` 改名为 `instructions.md`，正文内容保持；仅 `codebase-design/DEEPENING.md` 与 `DESIGN-IT-TWICE.md` 中三处返回入口的 Markdown 链接目标随之调整。其余上游内容逐字节保留，包括元数据、示例和 Bash 脚本。上述执行适配只在本文件列明，不写入原版正文。
