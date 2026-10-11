# 第一阶段最新真实 Agent 验收

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

最终状态 **BLOCKED**。真实模型 → Splash 读取工具 → 工具结果 → 模型回答 → 应用保存与显示的核心闭环已经实际通过。完整第一阶段没有宣布 PASS：普通干净 RC2 的 App Hub 仍不能直接发现并安装 script-tools 应用，且非法参数、服务超时、重复与迟到结果边界仍未验证。第二阶段业务开发未开始。

本文件是最新补充。工作区根目录三个 PHASE1 文件、原探针和历史失败日志均保留。此前前置复测文档已归档到 `docs/phase2/history/gate-before-consent-continuation.zip`。结构化证据为本目录 `PHASE1_EVIDENCE.json`，第二阶段证据包含相同最新记录。

## 环境、隔离与版本

沿用 `F:\CodexWorkspace\Projects\RipplePhase1-20261010`，分支 `experiment/phase1-real-agent-20261010`，HEAD `86b768adcd7823cc1efd6771612160b464b25378`。原仓库在 `F:\桌面\01 项目开发\黑客松\Ripple`，没有在 main 开发或发布新参赛包。

实际运行官方 Windows x64 [Desktop RC2](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.2)，源码 `4ccf8e068399b1da139771a9ed94cef05fa6ae60`，SDK 1.10.0。Shell SHA-256 `7d8027bc64618948dcef26b911978b444490034c49e010d6a87dd3d989cd55d0`；Kernel 为 `octos 2.0.3-rc.13 (b0759a5 2026-10-09)`，SHA-256 `5ffdbf58d86ab778d1436db4ddcea3621d67ec833c3959e75136b1323a6e02c0`。Hub 使用 RC2 固定源码 `95e4831afca7227b640f075b252c04355bb63865`。

发行包此前静态解包，SHA-256 与官方一致，隔离运行得到用户批准。此次没有重新下载、安装器、提权、系统配置修改或官方工具链补丁。Windows 11 x64、Ryzen 5 6600H 及 Git/Python/Rust/Cargo 的原环境记录保留在原报告。

Provider 为用户在宿主保存的 DeepSeek Official API / `deepseek-v4-flash`。Test connection 显示 Connected · 123 ms；真实工具能力由下述运行证明。继续使用原 `phase1/runtime/kernel-core`，未读取 profile 内容、host_binding 或密钥。无 Provider 测试只切换进程的独立空 core，随后恢复原 core，真实模型重启调用再次成功。

当前实验源码为 `phase1/probe-quota/bundle`，版本 **0.1.3-phase1**。同 id `ripple` 仅安装到专用 `phase1/runtime/phase2-gate-20261010-1027/quota-apps`，Shell 状态为同级 `quota-home`。原正式安装、旧 shell-home/shell-apps、repaired-home/repaired-apps 和所有负面测试目录完整保留。当前测试 Shell 已正常退出，Provider 仍保存。

当前已安装 manifest SHA-256 `0e5d3d37beaa0883fc7cfd8bd54fc9f7278ad4f45447dfd62f2a222ffc7f608b`，内容 digest `26915eb885f4be162a1de40322d1d34f4cd6fa09a5ca90794a87384fe6a7956b`。0.1.2 和 0.1.3 的源码内容相同、manifest 版本与配额不同，因此同 digest 不代表同运行声明；用 manifest 哈希区分。

## 真实运行

证据根目录 `phase1/evidence/phase2-gate-20261010-1027/`。以下均为实际模型调用，参数 `{}`。Kernel 别名 `ripple_context_read` 对应声明 `ripple.context.read`。模型 call_id 与 Splash token 不是相同字段，通过 session、turn、peer audit、工具内容、动态 retrieved_at 和模型回答关联。

| 场景 | turn_id | 模型 call_id | Splash token / 结果 |
|---|---|---|---|
| 有数据与界面保存 | `7df15e9a-dec4-4be3-9092-443e778692a1` | `call_00_A8Tt7bMEXhDTDBbbCBu28819` | script-tool-2 / ok |
| 操作者清空后重新读取 | `0b5fb54c-e3a6-4a75-935a-b228224c2f80` | `call_00_RNnvFUleaBn1j20Vt0TT8658` | script-tool-3 / ok，events=[] |
| 应用关闭后的原生 Ask 面板 | `e8dfac0a-0617-4d08-b96e-182321c482a3` | `call_00_lu5Qa1P5OLRGaCfBFVw79443` | 未执行 Splash / error:host:app_not_running |
| 恢复 Provider、重启后 revision 2 | `42e643a7-219d-48a0-9f1c-24c9ee5f8e6f` | `call_00_DmJ28PgJYNiSSSyRfcyU8650` | script-tool-2 / ok |
| 非法合成记录 end < start | `700d7eec-0ec9-45c1-9eb9-ce1b614e5eb4` | `call_00_OAM4M1qCJZvVPIk0E1SB4957` | script-tool-3 / error:host:app_error |

首次当前版 session_id 为 `_main:api:octosense#peerctx-ripple-22a12f906cd27b73.632ca874-p1-card-ripple-g1`；以 `quota-turn3-complete-kernel.json` 的原始字段为准，其他场景各有完整 session_id。当前版首次读取返回 event_id `ripple-test-1791634960-r1`，start `1791634960`，end `1791638560`，revision `1`，data_source `ripple-sandbox-synthetic`，retrieved_at `1791631360.417902`。

工具在执行时重新 fs.read 实际沙盒文件。Kernel tool_start/tool_end、peer audit、assistant_persisted 和 turn_completed 均存在；应用 phase1-turn.json 的回答与 Kernel 原文一致，六个表格字段逐项匹配。日程前后哈希相同。恢复后的读取返回不同 event_id `ripple-test-1791635088-r2`、revision `2`、retrieved_at `1791631606.8888793`，进一步证明结果来自当前状态。

实际关联自动检查结果在 `continuation-correlation.json`。原始记录分别是 `quota-turn3-complete-*`、`quota-empty-turn4-complete-*`、`quota-closed-turn5-complete-*`、`quota-restored-turn6-*`、`quota-invalid-turn7-*`。截图为 `quota-real-answer-ui.png`、`quota-empty-answer-ui.png`、`quota-closed-answer-ui.png`、`quota-restored-real-answer-ui.png`、`quota-invalid-answer-ui.png`。只有 Kernel 选取的工具与最终回答记录进入报告，未复制流式 reasoning。

模型额外生成的 UTC 换算有错误：首次当前版把实际 2026-10-10 的时间说成 2026-10-09。原始六字段正确，模型解释却不能作为可执行计划依据。这不是第二阶段模型结果校验通过；受限协议和独立时间校验尚未实现。

## 最小修复与真实故障

0.1.1 已有真实工具/模型记录，但 UI 保存失败。0.1.2 以源码 len()>8192 上界限制回答并保存历史计数；字符串长度单位与 UTF-8 字节长度未独立测量，仍在 `fs.write(phase1-turn.json,...)` 报 write failed；其实际 turn_id `b5b5d0bd-8195-4be7-be7c-6e9750593fe5` 和 call_id `call_00_FYrA5j61RKhidkI7ERo28120` 保留。

递归检查发现 RC2 在同一个应用沙盒的 accounts/device/contexts 下写入会话工作文件。0.1.2 根目录文件约 38 KiB，但递归总量为 **74,570 字节**，超过声明的 **65,536 字节**。证据 `repaired-storage-quota-root-cause.json` 仅记录路径和大小，不读取凭据。此前只看根目录而否定配额原因是不完整诊断，现已更正。

0.1.3 只把实验 manifest 的 storage.max_bytes 改为 **1,048,576**，工具函数、tools.json、AGENT.md 与旧探针一致。实际安装后真实回答持久化成功，错误复测和重启复测也成功；最终递归占用见 `quota-final-storage-usage.json`。没有增大官方上限或修改官方文件，长期会话增长仍需下一阶段处理。

本地 rehearsal 目录使用临时签名，正常通过官方 publish/verify 和宿主安装；它不是官方 App Hub 发布。私钥只在仓库外临时目录使用后删除。旧宿主拒绝新测试证书的历史失败仍保留，未更改其信任缓存。

## 安全边界

| 边界 | 实际结果与范围 |
|---|---|
| 拒绝 Agent | 0.1.1 专用负面宿主正常 Don't allow；allowed=false，重复 session.open 报错，无工具调用，日程哈希未变。门禁由宿主实现，0.1.3 工具未变；未冒充当前版重新拒绝实测 |
| 无 Provider、许可有效 | 0.1.3 同一 quota-home/app 数据，独立 `quota-no-provider-empty-core`，allowed=true；实际 SESSION ERROR / profile_unresolved；零新工具调用、日程和旧回答文件未变。旧回答文件不是本轮响应 |
| 空数据 | 操作者 Empty 后真实模型重新调用，返回 events=[]；模型明确无当前事件，不将历史事件冒充当前数据；文件保持缺失 |
| 应用关闭 | 正常打开宿主 Ask Ripple 面板，再关闭 Card；真实模型发起调用，host:app_not_running；Splash 审计无新增，日程未变；模型报告失败 |
| 读取实现失败 | 操作者注入 FIXTURE 非法记录 end < start；真实调用被 mod.app_tools.fail 拒绝；模型报告失败，记录未被 Agent 修改；操作者恢复原测试文件，恢复哈希一致 |
| 非法工具参数 | 未验证；非法记录不是非法参数测试，后续必须单独测试 Schema/宿主/工具拒绝 |
| 模型服务超时 | 未验证；后续需真实受控超时与取消，验证终态、未写入和恢复 |
| 重复请求与迟到结果 | 未验证；后续需关联不同 call_id/任务代次，验证重复点击、取消和迟到结果；代码 active 检查不等于运行通过 |

工具不写业务日程，但追加诊断日志，这是明确的磁盘副作用。操作者 Seed/Empty 和 FIXTURE 注入用于实验布置，未向 Agent 暴露。所有合成日程不称为个人日历，模型凭据仅宿主管理。没有执行或审批写工具。

## 普通冷启动与 ABI 阻断

当前普通启动命令只有 `phase1/runtime/rc2/octosense.exe`，无测试参数。使用新的 normal-cold-home/normal-cold-apps 和原 Provider core，从 Dock 正常打开 App Hub，**Ripple Phase 1 Lab 显示 Unavailable**。证据 `normal-cold-process.json`、`normal-cold-desktop-ui.png`、`normal-cold-apphub-ui.json/png`。这不是测试启动参数导致的假失败。

此前多次实际安装复现：启动无 Agent 的基线 Card 后，旧 Hub 刷新显示 Get，但安装仍报 `needs a host implementing app_tools.dispatch@1`；正常关闭重开 Hub 才成功。之后工具内 runtime.list/describe 返回 app_tools.dispatch implemented=true、supported=true、version=1、checked-on-use。两个观察同时真实成立，不能拿后一项覆盖前一项。

RC2 固定 Hub 的 CardModule 注册 ABI、Backend 初始化 Store 保存能力快照，与此现象一致。[所核对的最新 Hub 源码](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/7b36c8afc2e4bad9dfa5d77692b6fd453f0b9785/crates/app-hub-app/src/catalog.rs) 也仍在初始化时取 available_versions；这只是源码分析，未声称运行了最新源码。当前 [官方发布列表](https://github.com/OctoSense-org/OctoSense/releases) 所见 Windows 桌面最新为 RC2；Android Home beta2 不代表 Windows 修复。

解除条件：官方兼容宿主能在干净状态直接发现/安装/启动 script-tools 应用，或有经验证的正式支持路径。不得补丁修改官方门禁、伪造能力或把特殊启动顺序当普通 PASS。无需为只读 Agent 更换系统的证据已存在；更换平台本身能解决该问题尚未验证。

## 命令、检查与原版保护

启动参数和所有受控环境变量在 `*-process.json`。实际 Makepad HTTP 操作的时间、路径和响应大小在 `actions.jsonl`：/snap、/g?raw=1、/click、/m?k=scroll、/text、/quit。没有直接 dispatch 工具或通过脚本编辑许可文件。用户许可按此前批准的 Ripple 只读范围，在正常宿主许可界面处理。

本次实际执行的核心命令包括：

```powershell
python phase1/recheck_gate.py app-state repaired-before-turn2 repaired
python phase1/recheck_gate.py click-button "Ask real Ripple Agent"
python phase1/continue_gate.py capture repaired-real-turn2
python phase1/continue_gate.py usage repaired-storage-quota-root-cause
python phase1/prepare_quota_mirror.py
python phase1/continue_gate.py start quota-positive --quota
python phase1/recheck_gate.py click-button "Empty synthetic state"
python phase1/continue_gate.py start quota-no-provider --quota --empty-core
python phase1/continue_gate.py start quota-restored-provider --quota
python phase1/continue_gate.py start normal-cold --quota --normal-cold
python phase1/recheck_gate.py baseline original-delivery-integrity
python phase1/finalize_continuation.py
```

所有 Hub 签名/发布/校验命令与真实输出在 `quota-mirror-commands.json`。最终检查 `continuation-final-checks-v2.json`：源码 unsigned structural check、catalog verify、已安装包带受信发布者公钥的签名 check、Python py_compile、Git diff --check 均成功。unsigned 仅检查源码；实际安装包有签名，宿主没有 allow-unsigned 绕过。

保留一次 CLI 检查语境错误：对已发布的本地版本用 catalog-aware prepublication check，官方拒绝版本重复；改用已验证 catalog 公钥检查已安装包成功。保留两个文档辅助脚本 assertion 失败：第一次停止于上述 CLI 返回，第二次把本次 recheck helper 的合理改动误算原源码损伤。原报告/探针没有改变，初始 helper 已在 ZIP 中保存；修正检查范围后实际关联与源码检查成功。这些辅助失败不是模型错误，均未删除。

交付再次核对原仓库的 95 个文件、3 个原应用状态文件、历史构建清单、HEAD/tag/status/diff，全部与实验前一致，见 `original-delivery-integrity-comparison.json`。main / v0.1.0 / 原 HEAD 保留，原 main.splash SHA-256 `9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`。原版 63/63 自动测试、lint、typecheck/build 为此前第一阶段实际结果，本次没有重跑并冒充第二阶段测试。此次再次启动隔离原生基线。

回滚无需 reset 原仓库：所有受控宿主已正常退出，重新使用原正式仓库与原状态即可。保留 Provider/core、测试目录、历史版本和全部证据；后续启动现有 quota-home/apps 用新的运行 label，不能覆盖已有日志。

比赛冻结规则按 `gosimfoundation/hackathon-agenticapp26@600c32305f0e70261c91f01d328af73c0971e756` 的 [competition-schedule.md](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md)。10/9 23:59 冻结；本次 Agent 是冻结后未发布实验，不能宣称已冻结提交或新增评分能力。没有修改 Issue #94、推送、移动 tag、覆盖发布或联系主办方。
