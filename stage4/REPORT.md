# Ripple Stage 4 核查与有界验证 — 2026-10-12

**最终状态：BLOCKED。** 本阶段没有证明 Agent 比最早候选规则更有用，也没有独立操作者复现。按停止条件，**停止功能增强，重新审视产品定位**；不增加工具、提示词复杂度或外部系统。本轮不设目标分数，也不以重复测试次数换取评分。

## 基线、保护和改动

原始工作树 `F:/桌面/01 项目开发/黑客松/Ripple`，`submission/ripple-v0.1.0`，HEAD 与 v0.1.0 commit 均为 `86b768adcd7823cc1efd6771612160b464b25378`。其 bundle/main.splash SHA-256 为 `9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`。原先未跟踪的视频保持不动。

阶段三工作树 `F:/CodexWorkspace/Projects/RipplePhase1-20261010`，分支 `dev/stage3-quality-20261012`，HEAD `3ed5d32bca171f901072edac7bf479875b5c5413`。实际读取 REPORT、专项测试、失败日志和最终 manifest，逐个核对 manifest 中的源码/收据摘要。三个跟踪文件差异与已保存补丁字节相同，12 个未跟踪 stage3 源文件/文档匹配。

**先在项目外保全，后建立新副本：** `F:/CodexWorkspace/05-Backups/RippleStage4-20261012-1617` 保存 stage3.patch、12 个经核对的源文件/文档、版本清单及哈希。没有复制凭据、Provider 数据库、旧活动或会话内容到保全包。首次保全脚本遇到 Windows 默认 GBK 解码 UTF-8 清单失败，退出 1；改为显式 UTF-8 后继续，既有归档文件逐字节确认相同才复用，未覆盖。

Stage 4 独立 Git 副本为 `F:/CodexWorkspace/Projects/RippleStage4-20261012`，分支 `dev/stage4-value-20261012`。使用 `git clone --no-hardlinks --no-checkout`，没有 Git alternates，不是共享旧工作树。新副本先 checkout 基线，再 `git apply --check` / `git apply`；12 个文件在新目录以排他创建重放。新副本 push URL 已设为不可用值，原仓库配置未修改。

本轮新增内容全部在 `stage4/`：独立依赖准备、三轮 SDK 有界运行、空 Provider 原生 smoke、非秘密 ACL canary 检查、旧 AI 证据复核、试用说明和本报告。**没有新增业务改动**。相对 Git HEAD 的三个修改仍只是阶段三内容：`main.splash` +6 行，manifest 摘要更新，harness +72 行。stage3 目录在新副本是历史材料，不是 Stage 4 成功记录。

最终入口仍为 `stage1/bundle/main.splash`，manifest 版本仍为 `0.2.3-stage2`：

- SHA-256：`ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b`
- bundle BLAKE3：`1dc41555dee5c43f11690dcea7d0e937e05e95fdf08f0bb7e426c2c2a551f998`
- HEAD 仍是 `3ed5d32bca171f901072edac7bf479875b5c5413`，差异未提交，不能仅以 HEAD 代表完整当前源码。

最终基线保全结果见项目外 `protection-final.json`，检查 12,277 个既有文件及两个旧工作树的 refs/status/remotes。未执行 stash/reset/clean，未删除旧证据、提交、推送、公开发布或修改默认宿主信任策略。用户指定 ProviderSwitch 脚本仍不存在，未运行其他替代脚本。

## 产品技术状态

六行修复位于 `finish_verify` 的一致性检查之后：实际记录不匹配时先返回 PARTIAL；SAVE 分支先返回；RESCHEDULE 仅在输入时间仍等于收据 before.start 时同步已确认的 after.start。用户另改的时间不会被覆盖，标题及其他草稿不动；批准消费、唯一 write_event 写入口和独立回读没有变化。

**这不是仅靠静态判断：** 新副本从四份独立固定 SDK Git 源码构建，三个全新证据目录顺序执行原五项业务测试，分别 5/5、exit 0。专项覆盖标题保存不回退、立即保存、时间/标题草稿、显式改时间、拒绝、STALE、PARTIAL 不同步以及 boot/inspect；其余测试覆盖错误 ID、字段注入、未批准写入拒绝、迟到响应、重复审批/执行、存储拒绝和预报异常。天气与模型回复是明确 fixture，不称真实模型成功。

SDK 编译使用本机已有 Cargo registry 缓存和全新 target，不复用旧编译输出，也不修改旧 SDK。它证明本机新副本可构建，不能证明全新机器首次联网装依赖成功。

## RC2 与 RC6：本轮与历史分开

两个新宿主都使用复制并逐文件核对的官方发行资产、独立 home/app/core、新本地签名目录和仅该进程的测试锚。没有复制旧 Provider profile、数据库、会话或活动；没有修改官方 SDK/Kernel/宿主代码。输入都是本轮生成的合成活动，不是用户试用。

| 范围 | RC2 本轮 p4-rc2-clean-01 | RC6 本轮 p4-rc6-clean-01 |
|---|---|---|
| 冷 Hub 识别 | 识别 Ripple，Unavailable | 识别 Ripple，可直接 Get |
| 安装启动 | 普通 bootstrap Card 预热后成功 | 冷环境成功 |
| 保存、仅标题编辑、独立保存回读 | 通过 | 通过 |
| LIVE 天气 | 取得 Open-Meteo 快照 | 取得 Open-Meteo 快照 |
| 首次权限 | App Hub/Ripple 分别授权，失败后显式重试 | 同左 |
| 无 Provider | profile_unresolved / FAILED，无批准入口，无改期、零工具审计 | 同左 |
| Card 关闭重开 | 记录和输入一致 | 同左 |
| 宿主进程重启 | 经预热路径，记录和输入一致 | 直接打开已装 Ripple，记录和输入一致 |
| 新真实模型、两工具及批准改期完整闭环 | **未测试：空 Provider** | **未测试：空 Provider** |

保留了两次操作/驱动问题：RC6 安装后 Open 在滚动区上方，最初查找超时（该命令退出 1）；滚回顶部后正常。RC2 重启后两个相同图标排序变化，最初打开 bootstrap 导致 wait_card 退出 1；截图确认后打开实际 Ripple，检查通过。没有把这些失败计作无重试成功，也没有修改宿主规避。

阶段三 RC2/RC6 完整真实模型回归的收据与本次源码 SHA 确实相同，已读其 manifest 并核对摘要，但那些仍然是**阶段三历史验收**。不能冒充本轮真实模型重测。系统安装器、其他平台、全部网络异常和长期运行仍 NOT VERIFIED。原始 RC2 保留。

## SDK 异常与权限

为 `0xc0000409` 预先限定最多三轮全套、各自新数据目录，开启 RUST_BACKTRACE=full。本轮三轮均退出 0，未复现；不继续无限重跑。Windows Application 1000 事件确认阶段三 2026-10-12 14:42:39（北京时间）对应 harness，模块 `ucrtbase.dll` 10.0.26100.9444，异常 c0000409，偏移 0xa527e。只有模块/异常码，没有诊断调用栈，**根因 NOT VERIFIED**；不能由异常码名称断言 Ripple 发生栈溢出，也不能证明问题已修复。

两份新运行根的 ACL 只授权当前账户、SYSTEM、Administrators；测试文件是非秘密 canary。当前账户能打开，BU 受限令牌被 Access Denied (5)，读取字节为零。这验证目录的直接访问限制，不是另一个真实普通账户登录，也不是 Provider 正常授权成功。父目录替换/删除等完整路径保护仍未证明。

五份历史 Provider 文件与父目录权限不修改。用户先前明确拒绝本轮历史 ACL 调整，该决定持续有效；风险仍 BLOCKED，不重新请求同一批准。旧缺失 ledger/session 未重建。

## 用户价值与 AI 必要性

用户再次明确本轮无独立操作者：**USER_TRIAL_BLOCKED**。未收集或填写用户反馈，未伪造雨天、接受率或过去试用。`TRIAL_AND_REPRO.md` 提供可执行说明和空表。

`recheck_ai.py` 只读阶段三两个当前源码 run 的原始对照，先核对源码和 audit SHA，再对同一 context/weather/candidate 集合重新取最早候选：**10 条提案全部合法，10/10 与最早候选相同**。这里只重算十条旧观察，没有增加模型请求或真实试用。模型搜索后等待的历史观测约 2.29–3.76 秒；规则执行耗时没实测，不能声称倍数加速。原始用户约束和接受情况不存在，建议实际可用性未验证。

静态原因是现有 AGENT.md 明确偏向最早安全时间，候选算法按顺序最多返回前三个安全时段。十条候选起点跨度为 1 小时或 2.5 小时；并非让模型在全部可行时间中权衡。工具也没有个人空闲或偏好信息。因此目前证据支持“模型能按协议调用工具、选择合法结果”，**不支持“模型决策优于规则”**。

`DESIGN_DECISION.md` 的内部评估结论是不实施最小增强。缺少真实需求证据；即使将来需要硬时间窗口，也可能由规则完全解决，不能自动算 AI 增益。不为制造差异改提示词、不刻意选更差候选、不新增算法/审批/写入流程。

## 本届比赛可计分状态

2026-10-12 重新读取[官方赛程](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md)和[提交规范](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/app-hub-submission.md)，官方仓库 main 仍为 `600c32305f0e70261c91f01d328af73c0971e756`。赛程要求使用 10/9 23:59 冻结版本；阻断修复登记审核，不能增加获奖依据。

[公开 Issue #94](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/94)仍只有提交者演示补充和 10/9 入围评审两条评论，评审明确 v0.1.0/86b768ad。公开仓库 HEAD/main/tag v0.1.0 仍指完整 `86b768adcd7823cc1efd6771612160b464b25378`。App Hub 仓库 Ripple 标题/正文搜索只找到此 Issue；比赛仓库标题/正文搜索未找到 Ripple，不能据此推断私下接收是否发生。

可信证据支持该旧版曾提交并获初赛入围；仍无法核实 10/9 实际最终冻结回执或新版 Agent 正式接收。状态 **COMPETITION_VERSION_UNVERIFIED**。阶段三/四产品技术验证不能算作本届已获准能力，也没有联系主办方或补交包。最小解除条件是用户取得绑定完整 commit、时间和允许变更范围的可信回执。试用材料也不能倒填到冻结前。

## 命令与原始证据

所有相对路径基于 Stage 4 工作副本，`R2=stage2/evidence/runs/p4-rc2-clean-01`，`R6=stage2/evidence/runs/p4-rc6-clean-01`。新 evidence 不覆盖旧 evidence。

| 实际执行 | 结果/退出 | 证据 |
|---|---|---|
| 项目外 prepare.py baseline | 首次 1（UTF-8/GBK）；修正后 0 | 项目外脚本、baseline.json、stage3.patch；原始工具输出保留 |
| prepare.py clone | 0，独立 .git、无 alternates，补丁检查及重放成功 | 项目外 clone-command.json / independent-clone.json |
| python -B stage4/setup.py | 0，四份独立固定源码及官方发行资产 | evidence/clone-*.json、dependency-and-host-pins.json |
| python -B stage4/sdk_bounded.py | 三轮均 5/5、exit 0 | evidence/sdk-bounded-{1,2,3}.log、*-command.json、summary.json |
| 每轮 SDK 实际命令 | `cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1 --nocapture` | 对应 command JSON；RUST_BACKTRACE=full，全新 target / evidence |
| python -B -m unittest stage2.test_isolation -v | 0，8/8 | evidence/isolation-stage4.log |
| python -B stage4/recheck_ai.py | 0，旧 10 对重算，无新增模型调用 | evidence/ai-existing-pairs-rechecked.json |
| new_run.ps1、host.py prepare/start | 0；本地临时签名/镜像校验 0 | R2/R6 initialization.json、soak-*.json、*-process.json |
| native_checks.py begin/failure/reopen/verify | RC2/RC6 目标断言通过；上述两次 UI 查找/误点失败单列保留 | R2/R6 *-before.json、*-result.json、截图/state、actions.jsonl 的每次 UTC 请求 |
| stage4/acl_probe.py p4-rc2-clean-01 / p4-rc6-clean-01 | 均 0；非秘密 canary 拒绝受限令牌 | R2/R6 acl-access-check.json |
| Windows Application 1000/1001 只读筛选 | 找到两个历史事件，含一个具体异常模块记录 | evidence/sdk-windows-events.json |
| hub check 开发结构预检、语法及 git diff 检查 | 见 final-checks.json 实际退出状态；不是发行门禁通过 | evidence/final-checks.json |
| prepare.py verify | 见项目外 protection-final.json | 两旧工作树、12,277 文件保全 |
| 本轮宿主 /quit | 均返回 ok；对应 PID 退出确认见 manifest | R2/R6 actions.jsonl，evidence/hosts-stopped.json |

## 未满足条件与下一步

产品现状：原有审批/核验设计在本轮 SDK fixture 与原生已测路径未见回归；完整新 Provider/真实 Agent 闭环、真实用户可用性和独立复现仍未验收。SDK 未复现不等于修复；历史 ACL 仍有风险；LOADING 时取消按钮限制本轮未改。

最高评价的真实缺口是：真实独立需求与接受/拒绝记录、同事实约束下可观察的 AI 额外收益、别人可执行的源码和完整模型流程、长期异常证据、合法比赛版本。更多测试数量不能替代这些。

下一步先停止功能开发，由真实用户验证产品是否值得使用；若主要价值只是找最早无雨时间，应重新定位为有审批和回读的天气规则助手，Agent 保留为尚未证明必要的实验能力。只有获得确切需求和独立对照证据，才讨论一次最小增强。参赛版本回执与原始 ACL 处置由用户按各自边界另行推动，本轮不改。

回退不需 reset/clean 或覆盖：原始和阶段三工作树均保留，继续使用既有目录即可；Stage 4 运行进程退出后可原样保留审查。新副本也未提交或推送，无需移动任何 tag。后续如要重做验证，创建新运行编号，不复用已有验收文件。
