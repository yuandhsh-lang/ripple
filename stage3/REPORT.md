# Ripple 本轮质量验证报告 — 2026-10-12

**最终状态：BLOCKED。** 时间回写缺陷已复现、最小修复并完成 SDK、RC2 与 RC6 的本轮关键原生回归；本阶段整体未达到全部验收条件。严格内部模拟评分 **70/100**，不是官方决赛分数。真实用户、独立复现、历史凭据权限处置和新版赛事接收仍缺证据。未推送、公开发布、提交 Git commit、移动 tag 或替换冻结包；所有本轮改动仍留在独立开发分支供审查。

**版本与保全。** 原仓库 `F:\桌面\01 项目开发\黑客松\Ripple`，分支 `submission/ripple-v0.1.0`，HEAD / v0.1.0 指向 `86b768adcd7823cc1efd6771612160b464b25378`。原来未跟踪的 2:15 final 视频保持原状，未覆盖较早的已跟踪视频。远程为 `https://github.com/yuandhsh-lang/ripple.git`。开发工作树 `F:\CodexWorkspace\Projects\RipplePhase1-20261010` 起始及最终 Git HEAD 都是 `3ed5d32bca171f901072edac7bf479875b5c5413`；起始 main 干净，创建 `dev/stage3-quality-20261012` 后修改，main 未动。不能把当前未提交差异说成已存在的新 commit。

正式开发入口是 `stage1/bundle/main.splash`，manifest 仍为 `0.2.3-stage2`。起始 SHA-256 精确匹配用户要求：`7d08ba447ac9bd16bb2a08a049d9232c1d63329fc31764cf50d362cbe415223e`。最终源码 SHA-256：`ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b`。最终 bundle BLAKE3：`1dc41555dee5c43f11690dcea7d0e937e05e95fdf08f0bb7e426c2c2a551f998`。发布前完整版本固定仍待单独处理；本轮未获得比赛版本接收。

`evidence/protection-final-rc6.json` 实际复核 **9,184 个既有文件，变动 0**，原 HEAD、main、tags 和原工作区状态相同；五份历史 Provider DACL 也全相同。四个 SDK 源码工作区 `git status --short` 无输出。旧缺失 ledger/session 不重建，保留其历史缺失事实。官方宿主均为原发行文件，新进程用独立 home/app/core 和临时本地签名目录；只复制 Provider 配置，不复制会话、活动或 peer。用户指定的 ProviderSwitch 脚本不存在，未启用禁用副本。

当前仅一条候选搜索路径、两个只读 App Tools、一个 `write_event` 写入口，保存和批准共同使用它；天气完整性、STALE、审批、执行收据和独立回读机制均保留。根 `bundle`/旧 OctoScript 是冻结交付，`src` 是历史 React 原型，`phase1/phase2` 是实验与证据。历史副本不构成当前重复运行架构，未据此重构或删除。

**实际修改。**

| 文件 | 改动与原因 |
|---|---|
| `stage1/bundle/main.splash` | 仅增加 6 行：独立回读成功后，只有编辑框仍等于收据的旧时间时才同步新时间；标题及用户另改的时间草稿保留 |
| `stage1/bundle/manifest.json` | 用官方 hub stamp 更新摘要，不改版本、能力、工具或权限 |
| `phase1/business-harness/src/lib.rs` | 增加一个 72 行专项测试，覆盖时间回写、草稿、失败/STALE/拒绝及 boot；正式 Splash/SDK，明确使用 fixture 天气和模型回复 |
| `stage3/.gitignore` | 忽略新证据、下载及运行数据，避免凭据进入 Git |
| `stage3/protect.py`、`finalize_evidence.py` | 保全与实际收据聚合，不运行或改写历史应用数据 |
| `stage3/new_run.ps1`、`acl_probe.py` | 先保护全新测试目录 ACL，再复制配置；Windows 受限令牌执行只打开、不读取字节的权限测试 |
| `stage3/host.py`、`native_cases.py`、`run_matrix.py` | 复用现有隔离守卫与官方远程测试接口，固定 RC2/RC6 与基线/修复 bundle，逐项记录退出状态；无候选的人工天气 fixture 和回读故障注入明确分类 |
| `stage3/compare_ai.py` | 比较同一次工具返回的候选及模型选择，不产生另一套候选算法 |
| 本报告、`PROVIDER_ACL_REVIEW.md`、`USER_TRIAL_AND_REPRO.md` | 授权边界、待执行说明及空白试用模板；没有伪造已完成的试用记录 |

最终证据索引是 `evidence/final-manifest-rc6-supplement.json`，包含四组实际安装副本、bundle 文件、stage3 文件及收据摘要；差异是 `evidence/development-rc6-supplement.patch`。早先 `final-manifest.json` 与 `development.patch` 保留为 RC6 修复版补测前的检查点，不覆盖。回退只需继续使用未动的 main/原 v0.1.0；若要撤销修复，单独反向审查上述 6 行并重新 stamp 开发包。无需 reset、清理旧数据或移动 tag。

**缺陷、回归与实测边界。** RC2/RC6 当前版均指 `ce61...`。RC6 先以相同修复前基线 `7d08...` 验证，再以新 run `p3-rc6-after-01` 补测同一修复版；以下明确区分两轮。

| 检查 | 本轮实际结果与证据 |
|---|---|
| 旧时间回写 | SDK 修复前 exit 101；RC2 基线真实模型/实时天气批准后只改标题，确实退回旧时间。`evidence/sdk-before/editor-time-regression.json`；`../stage2/evidence/runs/p3-rc2-before-01/baseline-editor-result.json` |
| 修复后标题保存、立即保存、重复批准 | SDK、RC2 和 RC6 当前版通过；重复批准只有一次改期，显式保存可增加 revision 但不再次改期。RC2 `fixed-editor-result.json`、`fixed-editor-immediate-save.json`；RC6 `rc6-fixed-editor-result.json`、`rc6-fixed-editor-immediate-save.json` |
| 草稿、显式改时间 | SDK 测标题草稿和时间草稿，RC2/RC6 当前版实际编辑后批准、再显式保存通过。`fixed-draft-result.json`、`rc6-fixed-draft-result.json` |
| 拒绝、陈旧审批 | RC2/RC6 当前版与 RC6 基线真实模型流程通过；拒绝不写、保存使旧审批不可用。各 run 的 `*-decline-result.json`、`*-stale-result.json` |
| 回读不一致 | SDK 和 RC2/RC6 当前版通过；操作员仅对新测试记录注入不一致，显示 PARTIAL；检查不自动重写，恢复原测试写入后可再次核验。`fixed-readback-injection.json`、`rc6-fixed-readback-injection.json` 及对应 result。这是故障注入，不是自然发生的数据损坏 |
| 关闭重开 | RC2/RC6 当前版及 RC6 基线实际关闭重开 Card，记录及编辑框一致。RC2 首次脚本滚动早于新 Card 完成绘制而超时，保留失败，补充等待后核对通过：`fixed-reopen-result.json`；RC6 `rc6-fixed-reopen-result.json` 直接通过 |
| 模型分析中取消 | RC2/RC6 当前版及 RC6 基线通过，原记录不变。RC2 `fixed-cancel-analyzing-result.json`；RC6 `rc6-fixed-cancel-result.json` |
| 天气加载中取消 | **已发现限制**：按钮只处理中途 ANALYZING，LOADING 点击无效，之后仍可能出现待审批。没有自动写入。第一次 `fixed-cancel` 测试因此失败，不掩盖为通过；未扩展业务修复范围 |
| 无雨 | RC2/RC6 当前版及 RC6 基线均实际得到 LIVE NO_CHANGE，记录不变。`fixed-dry-result.json`、`rc6-fixed-dry-result.json` |
| 无候选 | 当前源 SDK fixture 通过；RC6 当前版原生、真实模型、**人工全雨天气 fixture** 得到 NO_CANDIDATE 且不写入。`rc6-fixed-no-candidate-fixture.json`、`rc6-fixed-no-candidate-result.json`。不是实时天气试用 |
| 模型坏 ID、恶意多字段、过期、存储/预报异常 | 当前源正式 SDK fixture 覆盖通过；本轮未全部在原生宿主复测，不泛化为 RC6 真实模型全异常通过 |
| Provider 不可用 | RC6 基线及当前版在各自新的空 `no-provider-core` / 新宿主进程返回 `profile_unresolved`，FAILED、零工具审计、活动不变；同时保留重启前记录。`rc6-missing-provider-result.json`、`rc6-fixed-missing-provider-result.json`。没有调用模型，不是远端 Provider HTTP 失败测试；RC2 修复版此项原生专测未做 |
| 长期稳定性 | 本轮有限场景通过，持续多日、远端服务断网/限流、宿主历史增长与真实多账户边界仍 NOT VERIFIED |

SDK 第一次修复后合并运行出现 `0xc0000409`（进程 exit -1073740791）；专项单独 1/1、原四项 4/4、全新合并重跑 5/5 均通过。**崩溃根因 NOT VERIFIED**，未改 SDK，也不把一次重跑当成长期稳定性证明。失败 log 全保留。

**RC2 / RC6。** 官方 RC2 路径保留；两次冷 Hub 都识别 Ripple 但显示 Unavailable，正常打开 bootstrap Card 后重新打开 Hub 才能安装。当前修复版真实模型闭环均来自该预热环境。RC6 官方 setup 文件 SHA-256 `4cced00c36fd613080368fcabb8af89ee80ed5aaf3bd3eaad5e3f19c02bbfa4d` 与发行摘要匹配；仅用 7z 解包，没有运行安装器或覆盖 RC2。RC6 `p3-rc6-before-02` 从干净进程直接安装与 RC2 相同基线 bundle，实际两个工具、审批、写入、回读、拒绝、STALE、分析中取消、NO_CHANGE、关闭重开、缺 Provider 失败均有证据；该基线也复现时间回写缺陷。第一次 RC6 尝试误点计算器，已单列保留并退出；冷安装结论仅来自全新第二次运行。

随后在全新 `p3-rc6-after-01` 冷 Hub 直接安装与 RC2 完全相同的修复版，`run_matrix.py` 九项顺序命令均 exit 0：标题保存/立即保存/重复批准、草稿、拒绝、STALE、分析中取消、回读故障注入、LIVE NO_CHANGE、fixture NO_CANDIDATE、关闭重开；另外缺 Provider 重启失败测试 exit 0。**RC6 只在这台 Windows、独立解包环境和上述矩阵范围内通过**。系统安装器、所有网络/模型异常、长期运行、独立首次复现仍未验证，不宣布普遍完整兼容，也不替换 RC2。共用旧驱动的启动打印仍写“RC2 started”；进程 receipt 的实际二进制路径/摘要及 stage3_host 才是版本依据，RC6 Kernel 捕获按 LIVE/FIXTURE 正确分类。

RC2 shell SHA `7d8027bc64618948dcef26b911978b444490034c49e010d6a87dd3d989cd55d0`，Kernel SHA `5ffdbf58d86ab778d1436db4ddcea3621d67ec833c3959e75136b1323a6e02c0`。RC6 shell SHA `bd1e55313d678dfba0f93968537294cfaf338350ad67b067ff265d9804903915`，Kernel SHA `dabb9293d378000baf9f132991e216a214bd00ba98a9160e4b3899946bff75da`。完整进程环境在各 run 的 `*-process.json`；没有修改宿主安全策略默认值。

**Provider 与真实用户。** 新测试副本先去掉普通用户继承权限，当前用户可打开，Windows BU 受限令牌返回 Access Denied (5)，真实模型成功亦证明合法宿主可读取该测试配置。此受限令牌不是另一个普通账户登录；后者 NOT VERIFIED。五份历史配置及父目录仍有普通用户权限，用户明确决定本轮不修改，保持 BLOCKED；精确范围及回退见 ACL 文档。未打印任何 Key 原值。

用户明确本轮无独立操作者，因此队外用户试用和独立复现均 BLOCKED。开发操作者的真实模型/天气测试不能代替队外反馈。已准备说明和空白模板；没有补写过去试用。**取消本轮可用时间窗口开发**，因为尚无真实试用证明它值得增加。

**AI 对照。** 当前修复版原生 RC2 的 **5 条可完整配对的 PROPOSE 样本**，5/5 使用真实返回的合法 ID，5/5 与同一候选集合中的最早候选完全相同；从搜索结果记录至模型选择多等待约 2.32–2.95 秒。RC6 当前版另有 **5 条可配对提案，5/5 合法且等于最早候选**，观测等待约 2.29–3.76 秒。这些是同一工程操作者的相关天气场景，不是十位用户，也不是随机对照性能基准。应用审计固定 24,000 字节上限，RC2 本轮末为 23,863 字节、RC6 为 23,839 字节，预算不足时跳过新日志；因此只统计完整配对记录，不能当成全部任务成功率。两宿主另有 LIVE NO_CHANGE 收据；RC6 的 NO_CANDIDATE 使用明确 fixture。RC6 基线 3 条提案也都是最早候选，单独保留、不充当修复版样本。详见三个 run 的 `ai-vs-rule.json`，包括 context、search、选择、时间及审计摘要。本轮没有观察到超越规则的选择增益，不能断言总体 AI 无价值，也不能虚构用户认为有用。实际可用时间约束和主观价值仍未测；当前 Agent 的作用已证实为调用工具和组织流程，必要性尚未证实。

**比赛合法性。** [公开 Issue #94](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/94)明确提交 v0.1.0 / 完整 `86b768...`，10/9 评审评论确认该版本初赛 75/100、入围。这纠正了“完全没有可信版本证据”的说法；但它不是 10/9 23:59 最终冻结回执，也未接收新版 Agent。[官方赛程](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md)要求决赛沿用冻结作品，阻断修复登记审核，不能增加获奖依据。当前 **COMPETITION_VERSION_UNVERIFIED**，10/9 实际最终冻结 commit 及本轮修复获准用于比赛均 NOT VERIFIED。

现有可公开归属 v0.1.0 的能力是实时天气、合成活动、规则改期、人工确认、写入与回读；新版用户活动和真实 Agent 仅可归属冻结后开发实验。能否在正式决赛计分仍需相应版本回执，不能用本地安装成功代替。没有发消息联系主办方。

[提交规范](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/app-hub-submission.md)要求公开源码固定版本、许可证、运行环境/说明、权限隐私、Agent 任务及验证材料；赛程明确复赛需队外试用、正常和失败验证。Hub 公开上架不是此前提，未签名本地预检不等于公开安装接收。任务自动化、可靠性、核验、人机协作、复现是评分因素；Kernel/ROM/生态贡献为自选技术贡献，Google Calendar、邮件、地图、多 Agent 都不是本项目的强制项。该规则明确不沿用旧固定权重；下列分数仅为内部诊断。

| 内部维度 | 分数 | 依据与缺口 |
|---|---:|---|
| 真实任务价值/体验 | 11/15 | 真正输入本地活动和实时天气；无队外需求证据，建议可能不符合本人空闲时间 |
| AI 必要增益 | 8/20 | 两个真实工具与合法结果已证；RC2 和 RC6 当前版各 5 条均等于最早规则选择，无可观察的选择增益 |
| 自动化及完成任务 | 18/20 | 分析、候选、批准、写入、回读闭环；任务范围仅单条本地活动 |
| 授权与独立核验 | 14/15 | 重复、STALE、拒绝、故障注入防假完成；原生异常矩阵非穷尽 |
| 稳定性与安全 | 7/10 | 本轮回归通过；历史 ACL、SDK 偶发崩溃、长期运行仍有缺口 |
| 宿主/首次复现 | 8/10 | RC2 预热、RC6 基线和修复版冷安装及关键矩阵通过；无独立操作者、系统安装器和长期验证 |
| 交付与真实证据 | 4/10 | 本轮证据可核对；新版接收、队外试用、独立复现缺失，当前差异未形成新 commit |
| 合计 | **70/100** | 与旧版官方初赛 75 不可直接相加或比较，不能预测评委打分 |

距 80 分缺的主要是实证：独立真实需求/可用性、AI 相对规则的实际收益、固定合法版本及独立复现。补证可能改善判断，但不承诺自动加 10 分。

**行动 A：无需改业务代码。**

| 事项与当前证据 | 比赛/用户影响与是否强制 | 最小方式及验收 | 稳定性/冻结风险 |
|---|---|---|---|
| 确认最终冻结和新版接收；只有 v0.1.0 公开评审 | 赛事外部 P0 阻断；固定版本及冻结规则为强制 | 用户自行取得绑定完整 commit 的赛务回执及修复边界；无回执继续 NOT VERIFIED | 不替换冻结包，不擅自补交 |
| 队外试用和独立复现；用户确认无操作者 | 试用是复赛交付要求，独立复现也是本轮验收要求 | 按空白模板邀请真实非开发人员，记录正负结果、原话和源证据；本轮 BLOCKED | 无代码风险；10/12 后材料不能冒充按时提交 |
| 历史 Provider ACL；5 个文件及父目录普通用户权限 | 本轮安全验收要求；官方未指定这种具体 ACL 实现 | 用户已拒绝本轮修改；之后只按精确批准范围备份 SDDL、保护、回退测试；还需真实普通账户与父目录完整性核查 | 环境 P1；可能影响读取，需保留回退；不改变参赛代码 |
| SDK 偶发崩溃、长期运行、干净启动说明 | 稳定性与复现评分因素，不能靠报告消除 | 保留失败日志；RC6 当前版关键矩阵本轮已补齐，剩余真实安装器/独立复现；SDK 崩溃若复现再定位 | 不改宿主/门禁，保留 RC2；测试不表示赛事接收 |
| AI 增益及交付叙述 | AI 决策价值评分因素，事实披露必要 | 当前如实报告两宿主各 5/5 相同；真实用户约束补齐后再对照，不调整答案 | 不新增算法，不夸大增益或冻结能力 |

**行动 B：局部开发。**

| 事项与证据 | 影响与是否强制 | 最小方式与验收 | 稳定性/冻结风险 |
|---|---|---|---|
| 旧时间回写，SDK + RC2/RC6 基线已复现 | P1 数据正确性；不是官方指定实现，但直接影响任务可靠性 | **本轮已修复**，只同步未被另改的时间输入；七项要求均有 SDK 和原生回归证据 | 业务 +6 行；仍属冻结后修复，需赛务审核才可用于赛事 |
| LOADING 时取消按钮无效，原生已观察、静态确认 | P2 体验与额外模型等待；不是官方指定功能 | 后续先决定是否仅禁用/说明此状态按钮；若要取消整个加载流程，仅扩展现有取消守卫并测晚回调，不建新状态机。本轮未实施 | 扩展异步取消会引入竞态，收益低于补证；冻结包不改 |

**行动 C：本轮不开发或不得修改。**

| 事项与证据 | 影响与是否强制 | 最小决策及未来验收条件 | 稳定性/冻结风险 |
|---|---|---|---|
| 可用时间窗口：无真实试用 | 可能提高实用性，但不保证 AI 增益；非官方强制 | 本轮取消开发。将来真实用户反复证明冲突后，再考虑最早开始/最晚结束两字段，并复用候选、旧方案失效、审批和唯一写入口 | 冻结后增强不可擅自纳入比赛；要测非法/空窗口/旧记录兼容 |
| 日历、邮件、地图、多 Agent、规划器 | 没有当前任务必须性，非强制 | 不开发；只有未来明确需求与数据授权才重估 | 增权限、外部依赖和回归面，无法补上缺失证据 |
| Kernel/门禁改造、强制升级、清历史 | 无必要；技术贡献是自选 | 不实施；保留 RC2、全部历史与证据 | 用户禁止，可能破坏隔离与冻结材料 |

执行顺序：先固定并审查本次差异及证据；由用户补版本回执与安排独立操作者；在已授权范围处理权限并完成独立复现；按同一事实做真实用户 AI 对照；最后才评估是否需要窗口字段或取消体验小修。**值得继续做验证，不值得现在继续扩功能。** 复杂框架、第二算法或外部集成不会自动提供 AI 收益、合法接收或独立反馈，反而扩大风险。

**命令、退出与证据。** 全部路径相对此工作树，`R2=stage2/evidence/runs/p3-rc2-after-01`、`R6=stage2/evidence/runs/p3-rc6-before-02`、`R6F=stage2/evidence/runs/p3-rc6-after-01`。官方远程 UI 的逐次请求和 UTC 时间保存在各 run `actions.jsonl`，截图与 state 为原始副本。

| 实际执行 | 退出/结果 | 路径 |
|---|---|---|
| `cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml editor_time_after_verified_reschedule -- --test-threads=1` 修复前 | 101，预期复现失败 | `stage3/evidence/sdk-before.log` 与 `sdk-before/` |
| 同 harness 全套修复后首次 | -1073740791 / 0xc0000409 | `sdk-after.log`、`sdk-after/` |
| 专项单独、原四项 `--skip editor_time_after_verified_reschedule`、全套新目录重试 | 0，分别 1/1、4/4、5/5 | `sdk-editor-alone.log`、`sdk-original-suite.log`、`sdk-all-retry.log` 及同名目录 |
| `python -B phase1/run_project_checks.py` | 0；npm test 126、integration 90（后者为子集），lint/typecheck/build 均 0 | `phase1/evidence/project-check-ryt776ji/commands.json` 及 5 份 log；这是本轮运行的历史 React 层检查，不代替 Splash 业务验收 |
| `python -B -m unittest stage2.test_isolation -v` | 0，8/8 | `stage3/evidence/isolation-tests.log` |
| `python -B phase1/check_sources.py` | 0，44 Python、6 历史实验结构；仅静态 | `python-syntax.log`；stage3 脚本另外由 finalize AST 解析 |
| `hub stamp stage1/bundle` | 0 | `bundle-stamp.log` |
| `hub check stage1/bundle --json` | 1，未签名正式门禁拒绝，符合预期 | `bundle-check.json` |
| `hub check stage1/bundle --allow-unsigned --json` | 0，开发结构预检通过，保留签名警告 | `bundle-dev-check.json`，不代表发布 |
| `stage3/new_run.ps1`、`host.py prepare/start` | 成功，官方临时本地签名/镜像校验 0 | 各 `p3-*` run 的准备命令 receipt；所有运行根独立 |
| `native_cases.py begin/finish/decline/stale/cancel/draft/readback/dry/reopen/provider_failure` | 上述矩阵与 JSON 断言为准；LOADING cancel 和首次 reopen 脚本超时退出 1，其余目标断言成功，`verify_reopen` 0 | R2/R6 及 baseline run；故障和补测不覆盖旧证据 |
| `python -B stage3/run_matrix.py`，RC6 当前版 | 0；9 个子命令均 0，完整命令/退出码分别记录 | R6F `rc6-fixed-*-command.json`、对应 log/result；fixture 天气明确区分 |
| `host.py start rc6-fixed-no-provider --reuse --no-provider`；`native_cases.py provider_failure rc6-fixed-missing-provider rc6-fixed-reopen-result.json` | 均 0；FAILED、无工具调用、记录保持 | R6F `rc6-fixed-no-provider-process.json`、`rc6-fixed-missing-provider-result.json` |
| `compare_ai.py ai-vs-rule.json` | 0，RC2/RC6 当前源各 5/5 相同；基线 RC6 3/3 | R2/R6/R6F `ai-vs-rule.json` |
| `acl_probe.py <fresh-run>` | 0，当前账户可打开、受限令牌拒绝 | 四个主 run 的 `acl-access-check.json` |
| 7z 解包 RC6 | 0；没有执行安装程序 | `stage3/evidence/rc6-extract.log`；官方 release JSON 与下载文件另存 |
| `finalize_evidence.py -rc6-supplement`、`protect.py verify protection-final-rc6.json`、`git diff --check` | 均 0；9184 文件未变 | `final-manifest-rc6-supplement.json`、`protection-final-rc6.json`、`development-rc6-supplement.patch`；早先检查点均保留 |
| 各测试宿主 `/quit` | 正常返回；只结束本轮创建进程 | 对应 `actions.jsonl`，未结束原有宿主 |

测试环境：Python 3.10.8、Node v24.14.0、npm 11.9.0、Rust 1.97.1。官方本地源码：App Hub `95e4831afca7227b640f075b252c04355bb63865`；Makepad `32d6415fb7476345ad36ee4f98d6f844d1f07fd2`；Octoscript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`；Octoscript-Makepad `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`。原始发行说明见官方 [RC2](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.2) / [RC6](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.6)。

剩余应用 P0：本轮未确认。已修复应用 P1：旧时间回写。剩余环境 P1：历史 Provider ACL、偶发 SDK 进程异常与长期稳定性证据不足；外部 P1：独立试用/复现缺失。P2：LOADING 取消体验、系统安装器验证及演示材料收敛。赛事外部阻断：最终冻结与新版接收 NOT VERIFIED。它们不合并成一个技术 PASS，也不由内部评分抵消。
