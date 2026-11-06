# Dev Workflow

将 Matt Pocock 的 12 个原版工程 skills 集成为一个开发入口，按需求大小编排完整流程。

用户只需调用 `$dev-workflow`。技能执行各阶段时读取仓库内对应的原版正文、模板和参考资料，无需另外安装或手工切换这些技能。

## 使用

仓库根目录就是完整的 `dev-workflow` 技能包。安装时保留整个目录结构，入口为 [SKILL.md](SKILL.md)。

```text
$dev-workflow 帮我开发一个设备预约系统。
$dev-workflow 修复这个功能在边界输入下的错误。
$dev-workflow 继续上次需求，先读取工作记录。
```

- 小需求：项目检查 → 明确目标与验收 → 实现或诊断 → 验证与审查 → 交付。
- 大需求：项目检查 → 需求澄清与确认 → 设计、规格及任务拆分 → 方案确认 → 实施 → 验证与审查 → 交付。

大小由影响范围、不确定性、复杂度和风险判断，用户可以纠正。大需求默认维护一份本地工作记录，主 Agent 按实际收益组织子 Agent 并负责集成验收；已有项目约定、用户修改和授权边界继续有效。

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
