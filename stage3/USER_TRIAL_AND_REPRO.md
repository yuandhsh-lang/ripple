# Ripple 后续真实试用与首次复现说明

本文件是待执行说明和空白记录模板。**本轮没有独立操作者；队外试用、独立复现均为 BLOCKED，下面不是已发生的记录。** 本轮原生测试由开发核查操作者执行。所有新增证据发生于 2026-10-12，不能冒充 10/9 前已提交材料。

当前开发分支 `dev/stage3-quality-20261012`；Git 基线 `3ed5d32bca171f901072edac7bf479875b5c5413`，本轮变更未提交。入口 `stage1/bundle/main.splash` 的 SHA-256 必须为 `ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b`；bundle BLAKE3 `1dc41555dee5c43f11690dcea7d0e937e05e95fdf08f0bb7e426c2c2a551f998`。完整文件摘要见 `evidence/final-manifest-rc6-supplement.json`，跟踪文件差异见 `evidence/development-rc6-supplement.patch`。这不是公开发行包或赛事接收凭据。正式比赛演示只能使用赛务确认的冻结版本；当前开发版 `COMPETITION_VERSION_UNVERIFIED`。

## 给试用者

不需要个人日历授权。Ripple 只管理你手动输入的一条本地活动；不会同步 Google Calendar、邮件或其他日历。输入的标题、时间、位置及天气与候选事实会通过宿主发送给你授权的模型 Provider；位置也会发送至 Open-Meteo。使用愿意分享的最少信息，不要填写敏感地点或他人信息。

1. 先自行写下确实可能参加的户外活动，以及可以和不可以参加的时间；不要为了配合建议改变自己的约束。由记录者单独保留原始约束，不向模型暗示测试答案。
2. 输入活动标题、未来七天内的开始时间、分钟时长和经纬度。**界面时间统一为 UTC+8，地点所在时区不自动换算。** 当前时长范围为 15–240 分钟。点击 Save activity，核对已保存面板。
3. 点击 Analyze with Agent。首次使用按宿主说明决定是否授权；若显示等待授权的 FAILED，处理宿主弹窗后显式重试。不要把授权后的重试算成第一次就成功。
4. 判断建议是否在自己真实可用的时间内，再自行批准或拒绝。无雨则如实记 NO_CHANGE。没有候选或失败也保留原结果，不为了展示成功反复换答案。
5. 批准后查看 COMPLETED、执行前后记录与独立回读；再仅改标题保存，检查时间没有回退。关闭重开后再次检查活动。拒绝后应保持原记录。
6. 用自己的话说明是否有用、是否理解“只修改 Ripple 本地活动”、等待与操作困难；记录原话，不请开发者代写正面评价。

**空白记录模板**（每次新建记录，不覆盖过去结果）：

| 字段 | 待真实操作者填写 |
|---|---|
| 日期、操作者代号、是否参与开发、记录同意 | 未填写 |
| Git 基线、源码 SHA、bundle 摘要、宿主/平台 | 未填写 |
| 活动事实、原先真实可用/不可用时间、时间区 | 未填写 |
| Provider 与天气来源 LIVE/FIXTURE；不记密钥 | 未填写 |
| 开始/结束时间、实际耗时、重试次数与原因 | 未填写 |
| 建议、用户能否参加、批准/拒绝及理由 | 未填写 |
| 最终记录、执行收据、回读与重开截图路径 | 未填写 |
| 失败/NO_CHANGE/NO_CANDIDATE、实际困难、逐字反馈 | 未填写 |
| 是否理解本地活动范围 | 未填写 |
| 是否存在反复的可用时间冲突 | 未填写 |

## 给独立复现操作者

修复版在本机 Windows RC2/RC6 独立进程中都已完成关键原生回归；RC6 先测相同修复前 bundle，再以新环境测试修复版。不能据此宣称所有平台和异常全兼容。官方安装程序仅解包运行；本轮没有测试系统级安装器。RC2 二进制保留在 `phase1/runtime/rc2`，RC6 隔离解包在 `stage3/runtime/rc6-extracted`。发行校验和、进程环境和二进制摘要见报告。独立首次复现仍待真实操作者执行。

必须创建全新的 Shell home、App data、Kernel core。不要复制旧会话、peer、用户活动或整个 Kernel core。独立操作者自行按官方 AI Providers 界面配置其有权使用的 Provider；不要分享本轮运行目录或凭据。新测试目录应只允许该用户、SYSTEM、Administrators，真实普通账户读取测试仍待补做。

本轮本地安装使用官方支持的临时签名目录和仅该测试进程的测试锚；用户已授权此范围。它不是公共 App Hub。`stage3/new_run.ps1` 只适合本机已授权的测试 profile 复制，不是对外分发脚本。`stage3/host.py` 复用现有隔离守卫，不修改宿主默认策略。真实首次复现仍应由操作者逐步执行并记录各项授权。

RC2 冷 Hub 会显示 Unavailable：先正常安装、打开同一测试目录里的普通 bootstrap Card，再关闭重开 Hub，才能安装有 script-tools-v1 要求的 Ripple。不要去掉 requires 或修改门禁。分别记录冷启动失败与预热后的结果。RC6 本轮冷 Hub 能直接安装，但这只证明本机该发行包的已测部分。

运行上面的正常流程，再至少运行拒绝或缺少 Provider 的失败流程。记录 `ripple.context.read`、雨天所需的 `ripple.slots.search` 的真实 Kernel turn/call ID、人工审批、执行收据和实际 `schedule.txt`；不把界面截图、fixture 或结构门禁单独当成闭环。

SDK 开发回归使用 Rust 1.97.1，设置 `MAKEPAD=headless`、`RIPPLE_TEST_ROOT` 为本工作树、`RIPPLE_TEST_EVIDENCE` 为全新空目录、`CARGO_TARGET_DIR` 为现有 harness target，运行 `cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1`。依赖是本机准备好的官方固定源码，完整四个 Git SHA 见报告。此测试用 fixture 天气与模型回复，**不验证真实模型成功**。第一次合并进程曾异常终止；重跑 5/5 通过，该异常必须披露。

AI 对照直接读取同一次真实工具返回的候选集合，将模型选择与其中最早候选比较，不另外计算天气候选。用操作者事先提供的约束判断两者是否可用，再评价是否值得额外等待；保留负面结果。只有真实试用反复暴露可用时间冲突，才重新讨论两个可选窗口字段。本轮不开发该功能。
