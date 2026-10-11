# Ripple 第一阶段阻断收敛验收

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

最终状态：**BLOCKED**。真实 Agent 核心闭环：**PASS**。完整第一阶段：**BLOCKED**。
本报告新增于隔离分支 `experiment/phase1-convergence-20261010`，保留此前资料，未发布任何正式版本。

## 官方上游与 A/B 对照

三个提交独立通过 `git merge-base --is-ancestor <SHA> origin/main`；抓取时官方主线为 `40ca21da68cc05ae930931adcfcf6d382d49ec26`。补丁全文、commit 信息和命令退出码在证据目录。
- https://github.com/OctoSense-org/OctoSense/commit/8ee0dad0b46a142d31dfe489fef37ecfe101d94d
- https://github.com/OctoSense-org/OctoSense/commit/3311d1a6156712ee7f8cb8f17bc892fb5155a470
- https://github.com/OctoSense-org/OctoSense/commit/dedd14a3e4eaaf384f137ee3ab0b8832378e2581

8ee0dad 提前注册 `app_tools.dispatch@1`；3311d1a 提前注册策略运行能力并新增进程隔离的冷启动回归；dedd14a 补全回归 manifest 的完整 integrity。实际查看 `crates/shell/src/apps.rs:883` 的官方测试，**没有改动该测试或门禁**。

| 项目 | A：原版 RC2，新空白数据目录 | B：dedd14a 官方源码构建 |
| --- | --- | --- |
| 源码/二进制身份 | 官方 RC2，SHA-256 `7d8027bc64618948dcef26b911978b444490034c49e010d6a87dd3d989cd55d0` | 精确官方提交已检出，源码 Git diff 空 |
| 不先开 Card，直接 App Hub | 已执行；Ripple 为 Unavailable | NOT TESTED |
| 冷态直接查询 runtime.list/describe | NOT TESTED：没有先开 Card 查询；Unavailable 不是直接 ABI 查询记录 | NOT TESTED |
| 直接安装完整 Agent 包 | BLOCKED：冷态不能安装 | NOT TESTED |
| 已安装包重启后直接打开 | 已执行；冷态打不开，先启动普通 Card 后可打开 | NOT TESTED |
| App Hub 能力快照无需重开 | 未通过；仍需重开 App Hub | NOT TESTED |
| 真实模型调用 | 预热后的 RC2 成功，含重新打开与重启后的新读取 | NOT TESTED |

官方源码最初多次出现 TLS/EOF/截断。通过官方 raw 内容和 HTTP Range 恢复，每个写入 Git 对象库的文件均核对 Git blob SHA，最终检出成功。使用稀疏检出，排除 `rom/`、`docs/`、`desktop/docs/`、`phone/docs/`，以及 31 个未获取到的图片/截图路径；完整范围见 `source-checkout-scope-final.json`。所检出的编译工作区、manifest 和目标官方回归源码均为官方对象内容，Git diff 为空；这不代表完整下载了上游仓库全部文件。
`python tools/setup.py --hub <现有缓存>` 获取官方固定 Octoscript-Makepad `6cf2d90aa33ff4ae603f49c7557f3ecf986207f0` 时长时间无数据进展，终止本任务拥有的 Git 获取进程；缓存未替换为旧版本。官方冷回归和 desktop build 实际执行，均 exit 101：缺 `.sources/makepad/code_editor/Cargo.toml`，**编译尚未开始**。因此不能判断官方修复回归通过，也不存在可用于 B 的新 exe。没有把本地修改宿主冒充 RC2。

## 真实闭环及时间修复

官方 Shell + Kernel `2.0.3-rc.13 (b0759a5 2026-10-09)` + DeepSeek `deepseek-v4-flash`。Provider 已复用，未读凭据、未重配。新实验包 0.1.4 与 0.1.5 通过未改动的官方 stamp/sign/publish/verify，发布仅指隔离本地镜像，临时签名身份不是官方发行签名。
0.1.5 首次真实 turn `db169299-f9e1-476d-a24a-b7b8d85fae81`，模型工具 call_id `call_00_WuvWisR3TJgy9HEkOfDg0167`，工具 `ripple.context.read`，risk=read，allowed，outcome=ok；模型回执含实际 Splash `read_token`，可与应用 audit、上下文任务 ID、工具返回及界面关联。更多实际 turn/call_id 位于结构化证据。

原模型把 epoch 1791634960 解释为错误 UTC 日期。程序唯一日程权威现为整数 Unix 秒 UTC；显示明确为 UTC 或固定 UTC+08:00。应用只接受 task_id/read_token/event_id/revision 四字段回执，并独立核对实际工具读取与当前文件内容；模型日期和额外字段不能进入日程/显示。
另外实际 VM 测试发现通用 shader `floor()` 的 f32 精度问题，现用 `t - t % 1` 保持限定有效范围内精度。90 个 Python datetime 独立金样本在真实 Splash VM 通过，覆盖 epoch 0、跨天、闰日、2038、2099 和非法边界。
真实结果 epoch 1791646786—1791650386 被程序显示为 UTC `2026-10-10T15:39:46Z`—`16:39:46Z`，UTC+8 `2026-10-10T23:39:46+08:00`—`2026-10-11T00:39:46+08:00`。Screenshot 与已保存 actual result 均存在。

## 异常逐项结果

| 测试 | 状态 | 证据类别/限制 |
| --- | --- | --- |
| invalid tool parameters/schema | PASS | HOST_PROTOCOL_INJECTION |
| tool execution deadline | PASS | HOST_PROTOCOL_INJECTION_AND_OBSERVED_REAL_MODEL_FAILURE |
| model/app request deadline | PASS | REAL_MODEL_WITH_OPERATOR_APP_DEADLINE_FIXTURE |
| Provider network timeout | NOT TESTED | No Provider/network configuration changed; app deadline cannot stand in for Provider transport timeout. |
| cancelled late model callback | PASS | REAL_MODEL_AND_HOST_PROTOCOL_INJECTION |
| duplicate tool requests/completion | PASS | HOST_PROTOCOL_INJECTION |
| duplicate analyze click | PASS | REAL_HOST_UI |
| continuous real conversations storage growth | PASS | REAL_MODEL |
| long-term quota exhaustion/retention | NOT TESTED | Five turns are not a lifetime test. Kernel conversations still grow inside the declared quota; retention not implemented. |
| closed app, reopen and Shell restart consistency | PASS | REAL_HOST_UI_AND_REAL_MODEL |
| model invalid Markdown JSON rejected | PASS | REAL_MODEL |
| wrong model UTC date/identity/changed revision/obsolete generation | PASS | DETERMINISTIC_FIXTURE_ON_REAL_SPLASH_VM |
| no Provider/permission refusal/empty data | PASS | PRIOR_PRESERVED_REAL_HOST_EVIDENCE |

必须区分 REAL_MODEL、HOST_PROTOCOL_INJECTION、DETERMINISTIC_FIXTURE；注入或 fixture 不计为模型工具选择成功。
官方 RC2-pinned App Hub `script_tools::tests` 实际 10/10 通过；独立 Ripple harness 最新 3/3 通过。该 harness 使用真实 SDK 队列、真实 Splash VM、实际文件与原处理器，额外私有 helper 只用于 fixture；不是新 Agent Runtime。`--no-default-features` 的组件测试仅关闭独立测试缓存缺少的可选 IME/text-input 集成，不能算完整 Shell 回归。所有失败尝试亦保留。

0.1.4 连续会话的第二轮实际触发脚本时间预算超限：Kernel 工具 30 秒超时，模型诚实报失败，程序拒绝回执，schedule 哈希不变。0.1.5 把可选诊断文件写入移到 `complete` 后，保持官方预算不变；随后有界连续 5/5 成功。重启后模型一次返回 Markdown fences，程序拒绝；以清晰的 raw JSON 用户指令重试后通过。这个限制不能称为模型永不出错。

取消真实任务及 2 秒应用请求 deadline 均收到真实工具事件，保存审计显示 `DISCARDED obsolete MODEL callback`；历史结果未变成当前结果，schedule 不变。2 秒来自 operator-only fixture，不是 Provider 网络超时。原始模型服务传输超时仍 NOT TESTED。

## 存储与原始项目

0.1.5 的连续 5 次真实任务存储 **32402 → 98560 bytes**，声明配额 1048576 bytes。失败版本的记录亦保留。Kernel 会话目录计入应用沙盒，诊断日志封顶不意味着 Kernel 历史封顶；无自动清理/长期配额耗尽验收。最终另含取消、deadline、重开和重启任务，共 197617 bytes（时间点见 receipt），不估算剩余轮数。
原始 Ripple HEAD/tag、未提交状态、95 个 tracked/untracked 文件（含原视频）、3 个旧应用状态文件哈希和历史 build 文件清单全部前后一致。原始 main/bundle/已冻结版本未修改；实验也未改既有审批状态机。独立 baseline Card 实际运行，原始数据目录未被用作实验状态；本轮未再次操作原始安装进行业务执行回归。

## 第二阶段安全范围

按本次最新请求，只读核心和原始完整性满足后，新增隔离 `phase2/readonly-prep/bundle`：`ripple.slots.search`。实际 ABI 测试调用了两个只读工具，并读取 FIXTURE 天气，最多三候选，复用旧 wet/coverage，程序产生 ID 与时间，独立重验上下文、天气内容/版本/有效期、未来/时长/用户边界。新约束产生新 search_id，旧 ID 失效；无解返回空，不写 schedule。
这只解锁只读准备代码；两个工具的真实模型规划、动态重新规划、AWAITING_APPROVAL 对接、LIVE 天气候选链、完整第二阶段均 **NOT TESTED / BLOCKED**。真实 Open-Meteo 单独 HTTP 200、完整小时区间、GMT/坐标已核验，未混入 FIXTURE 结论。
首选仍是官方 App Agent → tools.json → app_tool → mod.app_tools；Windows RC2 预热可运行，暂不能证明干净交付可复现，也不能断言必须换系统。第三阶段不应开始。

## 复现与回退

所有证据根：`F:\CodexWorkspace\Projects\RipplePhase1-20261010\phase1\evidence\convergence-20261010-1343`。关键实际命令/HTTP 操作见本目录 COMMANDS.json、证据的命令 receipts 与 actions.jsonl。编译版本/哈希见 final-bundle-hashes.json。当前所有本任务启动的 Shell 已用官方 `/quit` 正常关闭；Provider、应用数据、失败记录均保留。
复用已签名 0.1.5 镜像及其 receipt，在相同隔离 home/apps/core 下启动；原版 RC2 的预热顺序仍须如实记录。官方 B 需要先完成匹配 SDK 和 Cargo 图准备、通过官方冷回归并真正构建，之后再用独立全新目录完成 A/B；不能换旧 SDK 或修改门禁。
无需用户重新输入凭据。回退只需继续使用原始仓库/旧实验包；无需重置原始文件、删除数据或移动 tag。所有冻结后能力均为未发布实验，不属于 10 月 9 日冻结参赛包。
