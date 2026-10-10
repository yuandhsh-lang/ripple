# Ripple 第二阶段验收记录

**最终状态：BLOCKED。** 当前业务代码已完成五轮连续真实改期，核心安全回归通过；但“原有数据完整保留”的交付要求未满足：旧第一阶段测试账户中三份 Agent ledger/session 文件尚未恢复原始字节。不能把业务通过包装成整体 PASS。

项目 `F:\CodexWorkspace\Projects\RipplePhase1-20261010`，分支 `dev/stage2-stability-20261011`；开发基线 `d3b16bf066057e185324adea201cc2ad2924ce91`，第一阶段已有真实闭环，未重建。版本 `0.2.3-stage2`，实测 main.splash SHA256 `72b0ae1aaed2c5c403f817c9fd29a715123a3c55edb621121e84e61b90ef2acc`。最终本地提交与证据关联见 [acceptance-final.json](evidence/acceptance-final.json)。未推送、未公开发布。

## 实际修改与精简

- 修改 `stage1/bundle/main.splash`：复用原天气、搜索、审批、UTC、唯一写入口和独立回读；删除重复 `last_weather_fingerprint`、未使用的 last_read 字段、选择收据中的整份天气副本、无运行读取职责的 outcome.txt 写入。旧 outcome.txt 文件保留。
- 修改 `stage1/bundle/manifest.json`：移除正式代码没有调用的 `octos.session.history` 权限，版本及完整性摘要更新，保留原 1 MiB 限额和两个只读 App Tool。
- 修改 listing.json、PRIVACY.md，说明当前存储、数据来源和本地未发布状态；未改 UI 架构。
- 修改 `phase1/business-harness/src/lib.rs`：增加当前 SDK 存储、天气失败、错误模型回复、deadline、回读差异回归；仍明确使用 FIXTURE。
- 修改 `stage1/verify.py`：使测试 Kernel core 可注入，避免正式使用硬编码旧测试 core。新增 `stage2/.gitignore`、run.py、live.py、failures.py、acceptance.py、本报告；runtime/evidence 不纳入 Git。

没有删除源文件、历史实现或测试证据，没有新增依赖、后台服务、MCP、业务模块或 Rust 改动。删除项已经核对活跃调用，并经过当前 SDK 与真实 RC2 回归。正式入口仍是 `stage1/bundle`，根 bundle 是参赛冻结包，src 是历史 React 原型。

两个工具声明仍在 tools.json：implemented_by=app、risk=read、private_data=true。实现是 main.splash 的 app_tool/context 与 slots_tool/candidate_search；调用链仍为官方 `octos.session.open → octos.turn.start → mod.app_tools.request/active/complete/fail`。模型最终 data.text 只交接工具产生的 ID；确定性校验后在内存准备审批。没有执行工具，也没有第三个工具。

## 真实发现并修复的问题

| 问题 | 当前处理及证据 |
|---|---|
| SDK fs.write 会抛异常；原保存过程可能中断，未正确撤销旧成功状态 | 存储小适配器捕获异常；SAVE/RESCHEDULE 共用原记录 journal；先进入 SAVING/VERIFYING、预先安排独立回读，再写。`baseline-storage/` 保留失败；当前 `native-readonly-denied-comparison.json`、`native-quota-denied-comparison.json` 均 FAILED 且原活动 SHA 不变 |
| 原天气解析可能先覆盖缓存，之后才发现字段/小时异常 | 统一 valid_weather，验证响应、完整小时和活动覆盖后再保存；`vm-current-final/weather-failures.json` 九项拒绝，活动及此前天气均不变；真实缓存写拒绝 `native-weather-cache-denied-comparison.json` |
| 错误模型 JSON 和 deadline 的反馈不够可靠 | 错误 JSON 受控拒绝；90 秒当前 generation 到期进入 FAILED，迟到结果丢弃；`malformed-model-replies.json`、`tool-and-app-deadline.json`。这两项是 SDK/注入测试；真实取消迟到另有 native-cancel-late-state.json |
| 诊断日志/选择收据重复保存数据 | append 前校验完整新行不会超过24,000字节；选择收据仅保留关联ID、原/目标记录、时间和天气 revision；宿主 Agent 历史不清理 |

开发期间尝试过的全目录存储扫描在真实宿主上导致再次分析阻断，已撤回；当前没有该扫描逻辑。定额拒绝由真实 SDK 执行。中间失败日志全部保留，不计入当前通过项。

## 当前版本真实成功路径

官方 Windows Desktop RC2，Kernel `2.0.3-rc.13 (b0759a5 2026-10-09)`，`deepseek/deepseek-v4-flash`。使用验收人员通过 UI 输入的独立演示活动、Seattle 坐标及未来时间，LIVE Open-Meteo；没有个人日历或外部同步。以下五轮在同一实测源码上连续完成保存、实时天气、真实双工具、模型选择、审批、实际写入和独立 OS 读取。稳定 event_id `ripple-1791656864.895795`。

| 轮次 | 真实 turn_id | 活动 revision | 沙箱总字节 |
|---|---|---|---:|
| 1 | 56544b73-8b16-44c4-b067-b24c81d3f85e | 1→2 | 58,290 |
| 2 | dd22b6ec-aa10-42e6-a0f2-e2536931f867 | 3→4 | 86,341 |
| 3 | d4442ad8-93f5-41e3-a8a8-26f68bdee0ca | 5→6 | 129,981 |
| 4 | dbb93d48-a9b2-4182-9b47-28ed939098a1 | 7→8 | 158,227 |
| 5 | 87171389-2a07-47d8-b881-97bfe9a6d92d | 9→10 | 186,414 |

每轮 `evidence/soak-N-readback.json`、`soak-N-approval-kernel.json`、审批/结果 PNG 与 state.json 可关联模型、工具 call_id、候选、原记录、目标及落盘结果。第2轮连续点击批准，只增加一次 revision；第5轮 ANALYZING 中再次点击分析，没有重复改期。第3轮跨半小时边界，首次 slots 被程序拒绝，模型重新读取并搜索成功；原始拒绝记录保留，不声称所有工具尝试都成功。

## 测试分类与边界

| 分类 | 结果与记录（evidence/） |
|---|---|
| 官方 RC2 + 真实模型 + LIVE 天气 | 五轮 5/5；真实 NO_CHANGE：native-no-change-kernel.json、native-no-change-comparison.json |
| 当前原生失败路径 | 拒绝、源版本陈旧、一次真实重规划再拒绝、真实取消后迟到、Windows只读拒绝、满配额拒绝、天气缓存拒绝、空 Provider、关卡片重开不恢复审批，均活动 SHA 不变；对应 native-*-comparison.json 由 acceptance-final.json 索引 |
| 执行无法确认 | 实际 Agent/批准写入后，操作员仅对生成的测试活动注入回读差异，界面 PARTIAL，检查不重复写；恢复捕获的真实写入字节后检查才 COMPLETED。native-readback-mismatch-comparison.json、native-readback-unconfirmed.png。明确是故障注入，不计入五轮成功 |
| 重启 | native-restart-valid-comparison.json 验证 revision10；最终正常 Provider 环境 native-final-restart-comparison.json 再证 SHA一致，旧审批不恢复 |
| 真实 SDK / FIXTURE | vm-current-final.log：3/3；business-abi-results.json 包含无天气、无候选、陈旧天气/审批、重复执行、重规划限制等；90个 UTC/UTC+8 样本 current-time-vectors.json；HTTP/字段故障为九项注入，不能冒充真实服务故障 |
| 历史 React 自动回归 | project-tests.log：5文件63测试；lint/typecheck/build退出0。只验证项目指定目录；未限定目录的 npm test 曾扫描未追踪官方源码并失败，不声称全目录通过 |
| 静态 | soak-check.json：官方 hub gate passed，保留未签名开发包警告；真实安装使用独立本地签名镜像，main/tools/AGENT与实测源码哈希一致；Python编译、Git diff --check通过 |
| NOT TESTED | Provider真实传输网络超时；真实模型无候选分支（当前SDK/FIXTURE已测）；长期宿主历史留存；修复源码宿主构建及冷启动 |

真实天气曾不可用，UI 正确 FAILED，原始截图保留；该次助手比较未记录事前 SHA，`native-live-weather-unavailable-clarification.json` 已说明，不能据此宣称前后数据一致或确定网络错误种类。可核对的不变证据来自另列的原生拒绝及 SDK 测试。

## 限额、宿主与剩余问题

旧 32,402→98,560 字节来自 `phase1/evidence/convergence-20261010-1343/v15-soak-*`，统计整个应用沙箱，含账户会话目录，并非单个活动大小。当前五轮使用相同总文件字节口径。manifest 正式限额 1,048,576 字节；native-quota-measurement.json 在约284,453字节的生成沙箱内新增专用填充文件至精确上限，保存安全拒绝、原活动不变。测试填充文件移至新证据目录保留，没有清空旧数据。

- **P0业务缺陷**：当前已测路径没有发现会写坏活动或虚报 COMPLETED 的未修复缺陷；此结论不覆盖 NOT TESTED。
- **交付阻断**：三份旧测试 Agent 元数据未恢复，见下节；因此整体 BLOCKED。
- **P1环境/长期稳定性**：原版RC2干净冷启动 App Hub 仍显示 Unavailable，需普通 Card 预热再开Hub；`stage2-cold-hub`、`final-cold-hub`/warm记录保留。所有本次业务通过均标为预热环境。固定源码宿主 cargo check 退出101，当前最先缺失 `.sources/octoscript-makepad/crates/octoscript-makepad/Cargo.toml`，见 fixed-host-check.log。未改Rust或安装大型依赖。官方 [dedd14a](https://github.com/OctoSense-org/OctoSense/commit/dedd14a3e4eaaf384f137ee3ab0b8832378e2581) 是冷宿主测试fixture补全，不能据此宣布修复宿主已构建/生效。宿主历史仍增长，长期留存及Provider网络超时未验证。
- **P2**：首次原生 Agent 许可后需显式再次分析；listing的 example.invalid 是未发布测试占位，公开发行仍需真实隐私地址及人工许可。本轮不发布。

Windows在02:49异常重启，WER记录BlueScreen154；windows-bluescreen.json、windows-unexpected-restart.json。没有证据归因Ripple。之后实际重开、活动核对、回读差异、关卡片和无Provider测试已完成；不是等待重启验收状态。

## 原始保护与已知保留失败

原始 `F:\桌面\01 项目开发\黑客松\Ripple` HEAD仍 `86b768adcd7823cc1efd6771612160b464b25378`；main、两个tag、冻结包、95个文件、3个旧应用状态及历史build清单前后一致，原视频不变。既有根.gitignore未提交修改、历史未追踪开发文件未纳入当前提交。没有覆盖赛事包或改个人/生产日程。

**测试隔离存在一次失误。** 新Home/App目录起初复用了旧测试Kernel core。peer重注册后，保全核对发现旧第一阶段测试账户中六份宿主文件消失；三份找到SHA完全一致的副本并恢复，另三份ledger/session没有原始字节副本。对此不能声称“所有旧数据完整保留”。原阶段的schedule/执行收据和已捕获原始证据文件仍与基线一致，但它们不能代替缺失原文件。缺失路径、原SHA和恢复来源见 `metadata-exact-restoration.json`、`acceptance-final.json`。后续已改为独立测试core；只移动了该新core内复制的旧peer记录到新证据目录，未放宽权限、未改旧凭据。抱歉，这次隔离不足违反了保留要求。

保全最终比较覆盖1,442个历史文件，例外仅上述三份。最终判断：真实Agent、完整改期、清晰审批和可验证执行在当前预热RC2中已有证据；干净冷启动可复现性尚不成立，整体交付保留要求尚不成立。

## 核对与回滚

`python stage2/acceptance.py <新的收据名.json>` 只核对原始记录及当前源码，不替代实时运行。SDK回归仍使用既有Rust1.97.1、已准备的工具链，设置 RIPPLE_TEST_ROOT=项目目录、RIPPLE_TEST_EVIDENCE=新的空目录，执行 `cargo test --offline --locked --manifest-path phase1/business-harness/Cargo.toml -- --nocapture --test-threads=1`。原生实测复用 run/live/failures；证据文件均独占创建，不覆盖旧记录。

在本开发分支 revert 第二阶段本地提交即可撤销代码修改；不要reset/clean、删除新证据或把冻结包写进新版活动沙箱。代码回滚不能恢复上述三份缺失元数据，需要原始备份，不能用重新生成的文件冒充。
