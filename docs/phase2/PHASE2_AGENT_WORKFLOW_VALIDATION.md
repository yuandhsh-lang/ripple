# 第二阶段前置验收最终记录

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

**第一阶段完整验收 BLOCKED；第二阶段 BLOCKED，业务功能开发未开始。** 用户许可和 Provider 阻断已解除，真实只读闭环与应用回答保存已经验证。普通干净 RC2 App Hub 仍不能直接安装 script-tools 应用；非法参数、服务超时、重复和迟到结果仍未验证。因此按强制门槛停止第二阶段开发，第三阶段也不能开始。

## 当前交付与历史

继续使用 `F:\CodexWorkspace\Projects\RipplePhase1-20261010` / `experiment/phase1-real-agent-20261010`。工作区根目录 PHASE1 报告、原探针和全部失败材料保留。本文前一版和其他前置报告已保存在 `history/gate-before-consent-continuation.zip`，归档与逐文件哈希已核对。

最新第一阶段完整报告是 [PHASE1_REAL_AGENT_VALIDATION.md](../phase1/current/PHASE1_REAL_AGENT_VALIDATION.md)，决策是 [PHASE1_DECISION.md](../phase1/current/PHASE1_DECISION.md)。同目录 `PHASE2_AGENT_EVIDENCE.json` 与 `../phase1/current/PHASE1_EVIDENCE.json` 包含最新结构化证据；旧测试条目明确保留历史版本与复测关联。

## 实际宿主、模型和最小修复

实际运行官方 Windows x64 Desktop `desktop-v0.1.0-rc.2`，源码 `4ccf8e068399b1da139771a9ed94cef05fa6ae60`；Kernel `octos 2.0.3-rc.13 (b0759a5 2026-10-09)`；Hub 为 RC2 固定 `95e4831afca7227b640f075b252c04355bb63865`。复用已校验并批准隔离运行的本地发行文件，没有重新下载、安装器、提权或工具链修改。

Provider 为宿主管理的 DeepSeek Official API / `deepseek-v4-flash`。连接测试 Connected · 123 ms，真实工具能力由下面的 call_id 验证。原 `phase1/runtime/kernel-core` 和已保存模型完整保留；无 Provider 测试使用独立空 core，恢复后再次真实调用成功。用户许可通过正常宿主界面生效，没有编辑许可文件或伪造能力。

原 0.1.1、修复 0.1.2 都曾出现应用结果 `write failed`，失败日志完整保留。递归实测发现 0.1.2 的沙盒含 Kernel 工作子目录，占用 74,570 字节，超过 manifest 的 65,536。当前 `phase1/probe-quota/bundle` / **0.1.3-phase1** 仅在 0.1.2 基础上提高实验存储声明至 1 MiB，真实解决保存错误。最终实际占用 146,164 字节；长期会话增长未验证。工具实现、tools.json 和 AGENT.md 保持原只读工具。

当前已安装 manifest SHA-256 `0e5d3d37beaa0883fc7cfd8bd54fc9f7278ad4f45447dfd62f2a222ffc7f608b`；内容 digest `26915eb885f4be162a1de40322d1d34f4cd6fa09a5ca90794a87384fe6a7956b`。0.1.2 与 0.1.3 内容相同但声明不同，用 manifest 哈希区分运行版本。源码和安装包的独立校验见 `continuation-source-review.json`。

## 真实调用与关键异常

证据根目录 `phase1/evidence/phase2-gate-20261010-1027/`。以下全部来自真实模型，工具 `ripple.context.read`，参数 `{}`；自动关联见 `continuation-correlation.json`。

| 实际场景 | turn_id | model call_id | 观察 |
|---|---|---|---|
| 有数据闭环、应用显示 | 7df15e9a-dec4-4be3-9092-443e778692a1 | call_00_A8Tt7bMEXhDTDBbbCBu28819 | Splash script-tool-2，六字段匹配，应用回答与 Kernel 一致 |
| 空日程 | 0b5fb54c-e3a6-4a75-935a-b228224c2f80 | call_00_RNnvFUleaBn1j20Vt0TT8658 | events=[]，没有沿用历史事件冒充当前值 |
| 关闭应用后调用 | e8dfac0a-0617-4d08-b96e-182321c482a3 | call_00_lu5Qa1P5OLRGaCfBFVw79443 | host:app_not_running，Splash 未执行，模型报告失败 |
| 恢复 Provider、重启读取 revision 2 | 42e643a7-219d-48a0-9f1c-24c9ee5f8e6f | call_00_DmJ28PgJYNiSSSyRfcyU8650 | 新事件、新获取时间；这只是重新读取，不是重新规划 |
| 非法合成记录 end < start | 700d7eec-0ec9-45c1-9eb9-ce1b614e5eb4 | call_00_OAM4M1qCJZvVPIk0E1SB4957 | mod.app_tools.fail / host:app_error，模型报告失败 |

已许可但无 Provider 的当前版会话实际返回 `profile_unresolved`，零新工具调用，日程与旧回答文件哈希未变；旧回答文件不作为本轮模型响应。拒绝许可在原 0.1.1 专用负面宿主实际验证：allowed=false、两次 session.open 错误、零工具调用、日程哈希未变；未声称当前版又执行了拒绝测试。

所有上述只读调用都没有更改业务日程。Empty/Seed 和非法记录注入是操作员布置 SYNTHETIC/FIXTURE，工具只追加诊断日志。非法记录由操作员恢复，恢复哈希与注入前相同；不是 Agent 写入。

模型首次当前版额外生成的 UTC 日期有错误，原始六字段正确。**尚无第二阶段候选结果校验器来阻断这种模型解释错误。** 非法工具参数、服务超时、重复/迟到结果尚未验证；故障边界单项成功不能扩展为完整安全验收。

## 冷启动阻断与第二阶段范围

从新 `normal-cold-home/normal-cold-apps`，使用原 Provider core、无测试启动参数、仅启动 RC2 exe，再正常点 Dock App Hub，实验包仍显示 **Unavailable**。实际截图与进程命令见 `normal-cold-apphub-ui.png/json` 和 `normal-cold-process.json`。这排除了测试启动参数造成现象的解释。

此前实际复现：启动基线 Card 后，旧 Hub 刷新显示 Get，但安装报 `needs a host implementing app_tools.dispatch@1`；正常关闭重开 Hub 才成功。工具内 runtime.list/describe 的 ABI 为 implemented=true/supported=true/version=1。能力注册与 Hub 初始化能力快照的源码分析和现象一致，未修改官方门禁。特殊启动顺序继续作为交付风险。

没有实现 `ripple.slots.search`、自然语言候选选择、结构化结果校验、动态重新规划、旧提案失效或 Agent 到 AWAITING_APPROVAL 的对接。第二阶段 A–D 均未执行，E 的冷安装门槛未通过。不得把 revision 2 的重新读取称为反馈重新规划。成功率不跨版本、历史失败和负面测试估算，结构化证据为 null。

## 验证、原版与回滚

源码 structural check、本地签名 catalog verify、已安装包带受信发布者公钥的签名 check、Python py_compile、Git diff --check 实际成功，见 `continuation-final-checks-v2.json`。源码 unsigned 检查只用于结构验证，已安装包没有 unsigned 门禁绕过。此前 CLI 检查语境错误和辅助 assertion 失败均保留。

原仓库 main / `86b768adcd7823cc1efd6771612160b464b25378` / v0.1.0 与原未提交文件保持；95 个原文件、3 个原应用状态文件、构建清单及 Git 输出逐项相同，见 `original-delivery-integrity-comparison.json`。原 main.splash SHA-256 `9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`。此前实际 63/63 自动测试和构建资料保留，本次未重跑并计入第二阶段；此次已再次启动隔离的原生基线。

启动环境见各 process.json；真实官方 Makepad HTTP UI 操作在 actions.jsonl；命令与输出见 quota-mirror-commands.json 和最新第一阶段报告。所有受控 Shell 已正常退出；回滚只需使用原仓库和原状态，原仓库无需 reset。保留所有 Provider、状态和历史材料。

10/9 23:59 冻结规则来源为比赛源码 `600c32305f0e70261c91f01d328af73c0971e756` 的 docs/competition-schedule.md。本次 Agent 只能称冻结后未发布实验；未修改 Issue #94、推送、移动 tag、补交或覆盖发布。**目前无需用户重新输入凭据或再次许可；最小外部依赖是官方可复现安装支持路径。**
