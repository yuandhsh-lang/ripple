# Ripple 最终质量审计与验收

审计日期：2026-10-11。最终状态：**BLOCKED**。审计、修复和本地验收已完成；比赛版本确认及历史完整性仍有外部阻断。

## 1. 总体结论与真实基线

| 独立质量门槛 | 结论 | 依据与适用范围 |
|---|---|---|
| BUSINESS_QUALITY | **READY** | 当前开发包没有本轮确认且尚未修复的应用级 P0/P1。正式 Splash/ABI 回归及官方 RC2、真实 DeepSeek、LIVE 天气闭环通过。仅适用于声明的 Windows RC2 和已披露的宿主预热条件；不代表绝对无缺陷。 |
| COMPETITION_DELIVERY | **UNVERIFIED** | **COMPETITION_VERSION_UNVERIFIED**：存在仓库提交评论，但没有可信的 10 月 9 日冻结 commit 接收回执或新版 Agent 获准纳入决赛的证据。 |
| HISTORICAL_INTEGRITY | **BLOCKED** | 原始 Agent 元数据仍只恢复 1/3；另外两份没有可信原始字节。未重新生成或篡改哈希。 |

初始 HEAD 是 `ecc0cbcf68e36bc7bc81601eff401ecb05b9c2a4`，实际初始分支是 `main`，而非任务中预期的开发分支。`dev/stage2-stability-20261011` 指向同一 HEAD，已安全切换到该分支。第二阶段业务基线 `9f4557a8851259ee31b1eb9e57baf8a78b778f6b` 存在。已有 `.gitignore` 修改及历史未跟踪资料均保留，没有纳入本轮修复。

原冻结工作树 `F:\桌面\01 项目开发\黑客松\Ripple` 保持 `submission/ripple-v0.1.0` / `86b768adcd7823cc1efd6771612160b464b25378`。公开 main 也仍是该提交；原 tag 未变。指定 ProviderSwitch 脚本不存在，找到的是禁用文件，未重新启用、切换 Provider 或修改密钥。

正式开发入口始终为 `stage1/bundle`，版本 `0.2.3-stage2`；根 `bundle` 是冻结历史交付，`src` 是历史 React 原型。最终实际测试源码 SHA-256：`7d08ba447ac9bd16bb2a08a049d9232c1d63329fc31764cf50d362cbe415223e`；Bundle BLAKE3：`e0f3d00f383b7b140292989376d396f1b59184bb9b6ba4201ad7ae6b7de699c7`。SDK、最终原生运行包和正式源码字节一致。

证据根目录为 `stage2/evidence/runs/audit-20261011-final-01`（E1）与 `audit-20261011-final-02`（E2）。最终本地提交、工作树和文件版本记录见 [code-version-final.json](F:/CodexWorkspace/Projects/RipplePhase1-20261010/stage2/evidence/runs/audit-20261011-final-01/code-version-final.json)。证据不发布到远程。

## 2. 确认问题、根因、修复与复测

| 编号 | 等级 | 实际证据 / 根因 | 最小修复 | 复测及状态 |
|---|---|---|---|---|
| A01 | P1 应用 | E1 `sdk-before/final-audit-boundaries.json`：已批准写入后 Cancel 把状态改为 CANCELLED，抑制独立核验。取消入口仅检查 busy。 | Cancel 仅作用于 ANALYZING。 | E1 `sdk-final` 保持 VERIFYING；E2 `audit-final-approve-proof.json` 在实际 VERIFYING 时点击 Cancel，仍回读一致后 COMPLETED。**已修复**。 |
| A02 | P1 应用 | E1 `sdk-before`：截断活动记录的校验异常逃出 boot，SDK 中保留此前 COMPLETED。解析与完整类型校验未在同一异常边界内。 | `read_event` 包含读取与校验的异常捕获。 | SDK 5 种坏记录均保留并 FAILED；E2 `native-corrupt-comparison.json` 实际 RC2 截断重开 FAILED，无旧成功消息。恢复原测试字节后 READY。**已修复**。 |
| A03 | P1 应用 | E1 `sdk-before`：预报第六天合法雨天活动，搜索上界再加 48 小时，超过七天约束，被工具拒绝。 | 上界同时受实际预报末端及七天搜索跨度限制。 | E1 `sdk-final/final-audit-boundaries.json`：真实 SDK 工具读取合法第六天活动并返回有效候选。**已修复**。 |
| A04 | P1 应用 | E1 `sdk-deadline-before`：旧 90 秒规划计时器在批准写入后触发，显示 FAILED / 未修改，而实际已写入。 | 规划 deadline 仅作用于 ANALYZING。 | 最终 SDK 模拟旧 timer 在 VERIFYING 触发，继续核验并完成。未用真实等待 90 秒冒充本轮原生计时测试。**已修复**。 |
| A05 | P1 测试 | 原 `live.py` 强制要求审批；真实晴天 NO_CHANGE 会被错误判为失败。 | 区分真实决策与必须审批的雨天专项，接受 NO_CHANGE / NO_CANDIDATE 并核对活动未变。 | E2 `soak-1-readback.json`：真实 Seattle、DeepSeek、Open-Meteo 返回 NO_CHANGE，未批准、未修改，脚本通过。**已修复**。 |
| A06 | P1 测试隔离 | 原生坏记录验收中额外启动的隔离宿主 receipt PID 与实际 `/s` PID 不同；旧启动器只判断 API 有响应且可能超时仍报 started。 | 启动前拒绝端口占用；检查控制 API 的 PID；超时终止本次新进程并报失败。 | 8/8 隔离回归，包括实际占用 socket、乱 PID、无 API；实际修复后进程 46884 归属核对、原字节恢复与正常重开通过。**已修复**。 |
| A07 | P1 交付 | E1 `git-export-before.json`：Git 规范化改变 4 个包内文本字节，官方 Hub 因实际摘要不符拒绝；首次提交导出又发现三个未改内容文件仍沿用旧索引字节，见 `commit-export-before-restaging-check.json`。 | `.gitattributes` 为开发包保留盖章字节，并仅对 `stage1/bundle` 重新登记原始字节。 | E1 `git-export-after.json`：所有导出字节一致，官方 Hub 检查通过；最终提交导出再次核验。**已修复**。 |

没有确认新的应用级 P0。上述结论只覆盖已审查和执行的路径。

一般问题单独保留：E2 的提示注入标题任务确实调用了两个工具，但模型把 candidate_id 错放入 search_id，程序以 STALE 拒绝，活动保持原样。这不是成功改期，也不隐藏为通过。首次宿主权限确认后需再次显式 Analyze；批准完成后编辑框仍可显示此前输入，实际保存面板显示新时间；这些属于 P2 体验问题，本轮没有扩展 UI。

外部 / 历史事项：原版 RC2 冷 Hub Unavailable；缺失两份历史元数据；缺少冻结版本确认。它们没有被写成应用修复成功。

## 3. 真实修复及架构核对

- `stage1/bundle/main.splash`：只修改坏记录异常边界、候选上界及两个规划阶段控制条件。写入入口、整数 UTC 方案、审批和独立回读架构保持原有实现。
- `manifest.json`：仅更新官方工具生成的包摘要；权限、工具和版本没有扩展。
- `.gitattributes`：保留开发包实际测试字节。`main.splash` 提交保留实测 CRLF，因此普通 Git diff 显示较多换行差异；忽略行尾差异后仅有上述局部业务修改。`AGENT.md`、`listing.json`、`tools.json` 的运行内容与字节未改，提交变化仅修正 Git 中的换行字节，使其与已经运行的包一致。
- `stage1/verify.py`：控制端口和进程归属检查、启动超时，以及日志句柄关闭。
- `stage2/live.py`：接受真实无需改期 / 无候选结果，识别 EXECUTING、VERIFYING。
- `phase1/business-harness/src/lib.rs`、`stage2/test_isolation.py`：增加针对性故障和隔离回归。
- `stage2/final_audit.py`、`final_native.py`、`final_receipts.py`、`check_checkout.py`：本轮有限验收、保全和版本核对辅助，不进入正式应用运行路径。本报告为新文件，不覆盖旧报告。

没有新增依赖、后台服务、业务功能或 Agent 框架，没有修改 Rust Kernel，没有删除历史代码或证据。正式实现只有一套候选搜索、两个私有只读 App Tools、一个内存审批对象及共用的持久化写入入口。历史 React / 旧脚手架仍作为历史资产；未发现它们被开发包引用。Ripple 只管理一个活动，不拥有系统日历或其他日历权限，也不能据此宣称外部日历无冲突。

## 4. 本轮测试与真实使用验收

| 类别 | 本轮实际执行结果 | 证据与限制 |
|---|---|---|
| 官方 Windows RC2 | Kernel `2.0.3-rc.13 (b0759a5 2026-10-09)`；保存、审批、批准、拒绝、陈旧审批、存储失败、坏记录和宿主重开已运行 | E1 `kernel-version.json`；E2 原生快照 / state / comparison。业务通过均为预热环境。 |
| 干净冷启动 | 两个新 runtime 的冷 Hub 都出现 Unavailable；Card 预热后可用 | E1 `audit-cold-hub` / `audit-warm-hub`；E2 `final-cold-hub` / `final-warm-hub`。**没有干净冷启动 PASS**。 |
| 真实 DeepSeek | 共捕获 7 个真实工具任务 turn：过渡源码 2 个，最终源码 5 个 | 最终 5 个分别为 NO_CHANGE、模型无效 ID 被安全拒绝、DECLINED、COMPLETED、审批中修改后的 STALE。不是“5/5 改期”。HTTP 请求次数、费用和 Token 数未测量。 |
| LIVE Open-Meteo | 应用每次 Analyze 实际刷新天气；真实干燥返回 NO_CHANGE，真实降雨通过双工具产生候选 | E2 天气 / 工具 / Agent 日志。城市原始天气选样只用于输入未来活动时间，没有向应用注入天气。 |
| 最终批准闭环 | 同一 event_id，revision 4→5；预期对象与独立 OS 读取完全一致，才显示 COMPLETED | [原生批准证明](F:/CodexWorkspace/Projects/RipplePhase1-20261010/stage2/evidence/runs/audit-20261011-final-02/audit-final-approve-proof.json)，turn `a18ebb6e-816c-46cb-8502-c3f692c028d1`。 |
| 拒绝 / 陈旧审批 | 拒绝不写；审批中用户显式编辑到 revision7 后旧按钮消失、旧方案不写 | E2 `audit-decline-readback.json`、`audit-stale-readback.json`。 |
| SDK / FIXTURE | 4/4，0 ignored；正式源文件进入固定 SDK VM 与实际 App Tool ABI | E1 `sdk-final.log`、`sdk-final-version.json`。天气及模型回复明确标为 FIXTURE，不是真实模型。 |
| UTC 时间 | 90/90，实际 Splash 结果与独立 Python datetime 对照 | E1 `sdk-final/current-time-vectors.json`；保留整数 UTC，UTC+8 仅输入 / 展示。 |
| 输入 / 天气边界 | 10 类非法输入不写；5 类坏记录保留；9 类天气失败保留旧预报与活动；预报末端、空候选、缺口、过期等 SDK 回归通过 | E1 `sdk-final` 内业务、天气和边界记录。 |
| 存储 / 重开 | SDK 与实际 RC2 的配额拒绝、Windows 只读拒绝均保留活动；实际坏记录重开 FAILED；还原本轮测试原字节后 READY；旧审批不自动恢复 | E2 `native-quota-*`、`native-readonly-*`、`native-corrupt-*`、`native-restored-final-comparison.json`、`audit-restart-readback.json`。只修改新测试沙箱。 |
| 项目自动化 | 63/63，5 个测试文件，0 skipped | E1 `project-tests.json`，本轮运行；属于 React / domain 历史路径，不能替代正式 Splash 的 4 个回归。 |
| 隔离回归 | 8/8；两个 runtime 的实际 peer/context cwd 均在各自目录内 | E1 `isolation-port-clean-final.json`、`runtime-ownership-final.json`。每个 runtime 使用唯一 RIPPLE_TEST_RUN，通过 run.py 初始化与 verify.py 验证。 |
| 静态 / 构建 | npm lint、typecheck、build 均 exit0；Python 编译、Git diff 检查通过 | E1 `lint-final.json`、`typecheck-final.json`、`build-final.json` 及 compile/diff receipts。 |
| 打包一致性 | 本地源包及 Git 导出包通过官方 Hub；最终提交导出再检查 | E1 `final-bundle-check.json`、`git-export-after.json`、`commit-export-check.json`。unsigned developer warning 保留，不等于正式发布签名验收。 |
| 有界重复 | SDK 5 次规划 / 拒绝，busy 均释放、活动不变；日志增长止于 23,979 bytes，未超过 24,000 限额 | E1 `sdk-final/final-audit-boundaries.json`。宿主对话历史增长不由 Ripple 24 KB 限额控制。 |

安全不变量的对应依据：

| 不变量 | 已验证证据 |
|---|---|
| 无明确审批不执行；拒绝不写；不存在模型写工具 | SDK `no_approval_no_write` / `unknown_write_tool_denied`，原生审批前记录、拒绝回读。Save activity 是另外一个明确的用户写操作。 |
| 提示注入不增权；模型不能自报成功或自由生成执行日期 | SDK 注入标题原样作为活动数据，未知工具被拒；原生注入任务候选 ID 不符被拒；仅工具候选及程序构造对象进入执行。 |
| event_id / revision / 原记录不符、旧天气、过期候选不能写 | SDK guard 清单与最终原生 STALE；执行前重新核对原字节、ID、revision、标题、位置、时长和天气。 |
| 重复批准 / 重复执行不重复改；取消后迟到与旧代结果不获权 | SDK double approval、duplicate execution、cancelled late choice、old_generation_discarded；批准消费 proposal 后才写。 |
| 超时不批准；批准后的取消 / 旧规划超时不能抑制核验 | SDK workflow expiry 与两个新状态回归；原生 VERIFYING 中取消后完成。 |
| 写入结果未知不重写；回读不符不 COMPLETED | SDK 隐藏已写记录模拟丢结果 / 回读失败：PARTIAL，无重复写；恢复后仅 inspect；实际批准独立读取与异常存储记录。 |
| 坏记录 / 配额 / 只读失败保护已有活动；缺失天气不作无雨 | SDK 故障注入及上述实际 RC2 存储比较；无效天气拒绝覆盖。 |
| 无额外权限、敏感配置未进入审计范围输出 | 固定 tools/manifest、真实 host 许可记录、609 文件文本扫描无检出；局限见下。 |

明确 **NOT TESTED / 未验证**：真实 Provider 传输超时与抓包；真实模型 NO_CANDIDATE（SDK 已测）；同一宿主完成回调的重复网络投递；真实等待 90 秒后与写入碰撞（SDK 已测）；进程写入中被强杀、OS 断电与物理磁盘满导致中途部分写；数天持续运行的内存峰值、宿主历史留存上限和配额；Linux/macOS；真实 Google Calendar、OAuth 或其他第三方集成。没有将这些写为已确认漏洞或 PASS。

609 个文本文件执行了已配置凭据原值的内存比较和常见令牌格式扫描，无检出。排除了合法 Provider 配置存储，不输出密钥。实际工具活动字段与声明一致：schema、ID、标题、UTC 起止、坐标、revision、来源；没有读取无关旧用户活动。已查看本轮关键 UI 截图，但未进行全量 OCR 或传输内容审计。[扫描记录](F:/CodexWorkspace/Projects/RipplePhase1-20261010/stage2/evidence/runs/audit-20261011-final-01/privacy-scan-complete.json)。

## 5. 比赛合规与版本一致性

规则以本轮只读取得的官方规则 commit `600c32305f0e70261c91f01d328af73c0971e756` 为依据。[比赛安排与冻结要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md)规定正式决赛沿用 10 月 9 日冻结版本，阻断修复须登记前后证据并按审核规则处理；[应用提交要求](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/app-hub-submission.md)要求公开源码、固定版本、应用信息、运行和隐私等材料。

| 要求 | 核对结果 |
|---|---|
| OctoSense / OctoScript、App Tools ABI | 当前开发包符合声明的 script-tools-v1；正式 RC2 已实际运行两个私有只读工具。没有用当前 main 的未证明能力替代目标宿主。SDK 固定 Hub `95e4831`、Makepad `32d6415`、OctoScript Makepad `33dea2f`。 |
| 权限 / 数据来源 / 平台 | manifest 的 storage/runtime/session/turn/net 对应实际代码；应用直接网络目的地仅 Open-Meteo，Provider 由宿主管理。Windows 是唯一声明平台。 |
| Agentic 完整任务 | 当前开发包有用户输入、真实上下文、多步工具、有效方案、人工审批、程序写入和独立核验；拒绝、陈旧、失败状态可追踪。公开 v0.1.0 没有这些真实 Agent 能力。 |
| Apache-2.0 / 公开源码 / tag | 根 LICENSE 和公开旧源码 / v0.1.0 存在。当前开发修复仅本地固定提交，没有擅自推送。 |
| manifest / tools / 图标 / 截图 | 当前开发包资料存在、结构检查通过；本轮实际截图对应最终源码。原提交材料与旧包保持原样。既有 listing 截图没有独立的最终提交接收关联，不能声称决赛录屏完全同版。 |
| 启动 / 安装 / 无网络 / 无 Agent | 本地已有固定宿主及隔离步骤，源码和既有证据说明失败不会写。实际安装须预热；原版冷启动限制仍在。无 Provider 原生旧证据只作为未变路径参考，本轮没有重复运行。 |
| 新隐私披露 | `stage1/bundle/PRIVACY.md` 已准确说明 Analyze 后向模型发送标题、时间、坐标及工具事实，本地存储与日志、宿主历史、密钥管理和拒绝不写。无需重写。冻结版隐私说明未改。 |
| 正式公开隐私 URL | 开发 listing 仍为明确标注的 example.invalid，占位地址不能当作正式发布端点。正式发布前须按授权提供真实政策地址。 |
| 仓库提交证据 | [2026-10-06 的提交评论](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-6012523708)实际包含 Ripple 仓库 URL；纠正“完全没有提交评论”的旧认知。它不绑定冻结 commit，也不是新版接收回执。 |
| 10 月 9 日正式冻结版本 | **UNVERIFIED**：无法据现有材料证明赛事实际收到哪个 commit、是否含真实 Agent，以及后续修改是否已获批准。 |
| 预选通过 / 队外用户试用 / 决赛同版视频 | **UNVERIFIED**：在本次范围内未找到可信的对应确认。旧 171 秒视频是旧版演示，不能证明本地新 Agent；操作员验收不算队外用户试用。 |

已确认的交付差异：公开 main / v0.1.0 与本地新版功能不同，当前新版没有远程发布，公开隐私 URL 为开发占位。不能把这些差异自动解释为赛事已接受或已拒绝新版。

**当前不能宣称新版 Agent 功能允许用于正式决赛展示。**需要赛事方确认正式冻结 commit、版本接收情况、阻断修复登记及演示边界；如不获批准，应以确认的冻结功能为准。没有擅自替换包、提交登记、联系他人或发布。

官方技术资料只作为依据：[OctoSense](https://github.com/OctoSense-org/OctoSense)、[App Flow](https://github.com/OctoSense-org/OctoSense-App-Flow)、[App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)。实际宿主行为和本轮记录优先于未实测的新分支能力。

## 6. 遗留限制

1. 历史元数据维持 1/3。已恢复共同 ledger 的 738 字节 SHA 为 `366567fd179461761047e3c43d178f09c5bd2b0d8746dbe59d1215dd122b0cf4`；另两份 9d991bcd ledger/session 仍缺失。只检查存在性与既有 SHA，没有再次扫描同一批备份或造替代内容。
2. 原版 RC2 冷 Hub 仍可能 Unavailable。Card 预热是本轮如实使用的运行条件；没有修改官方 Rust，没有证明官方源码修复已在原 RC2 生效。
3. 当前只管理一个 Ripple 本地活动、按 UTC+8 输入时间，以坐标请求天气。没有系统日历同步、地名解析、外部日历冲突检测或第三方接入保证。
4. 模型可能返回不合格 ID，本轮实际出现一次并被安全拒绝；可以显式重新分析，但没有为了好看而绕过校验。Provider 与天气服务仍是外部可用性依赖。
5. 应用诊断记录有界，宿主历史仍增长；短轮次和存储拒绝测试不能证明长期内存或磁盘使用有界。

## 7. 保护结果、版本交付与回滚

[保全记录](F:/CodexWorkspace/Projects/RipplePhase1-20261010/stage2/evidence/runs/audit-20261011-final-01/protection-delivery.json)核对 5,204 个基线保护文件，非授权变化为 0；原冻结工作树、原应用状态、历史构建清单一致，tag 未变。测试仅使用两个新独立 runtime；只复制合法测试 Provider 配置，不复制旧 core 数据库、peer、workspace、活动或会话。新 peer/context 的实际 cwd 均属于对应新目录。

冻结参赛包未覆盖，原 Git 历史及 tag 未破坏，原始证据未删除，用户数据未清理，未执行 reset --hard、clean、强制覆盖或全目录删除。未远程推送、部署、发布、修改生产资源、DNS、密钥或数据库。测试结束后本轮 RC2 进程已退出。曾经误连旧的本轮进程及修复前失败日志均保留，没有隐藏为成功。

本轮两个本地提交只包含修复、字节保留、测试辅助和报告；已有 `.gitignore` 与历史未跟踪资产保持原状。实际最终提交导出经官方 Hub 再核对，为本地可复现开发版提供证据，不代替赛事接收证明。首次提交导出失败及后续补正记录完整保留。

如需回滚，在该开发分支审阅后，按反向顺序 revert `code-version-final.json` 的 `audit_commits` 中两个本地提交，不重写历史、不清空运行目录。若回到旧版，应使用另一个独立沙箱，避免旧 schema 覆盖新版活动。证据和用户数据不随代码回滚删除。

## 8. 最终建议

当前无需继续扩展或重构代码。本轮确认的 7 个 P1 已修复；当前开发版在已披露的预热 Windows RC2 条件下，可作为可核验的单任务户外天气改期 Agentic App 使用。没有已知未解决的应用级 P0/P1，不等于所有攻击路径、长期运行和外部服务都已证明无缺陷。

下一步需要取得赛事冻结版本与修复登记确认、对应同版演示和队外试用证据。当前尚不具备“正式决赛版本已被接收且完整可复现”的证据。

没有新可信原始字节时，不值得继续重复恢复两份历史会话；不应为本次验收增加日历 OAuth、多 Agent、地图、后台服务或修改官方 Rust。长期宿主留存及冷启动交由官方宿主修复与另行验证，保持当前复杂度和透明限制。
