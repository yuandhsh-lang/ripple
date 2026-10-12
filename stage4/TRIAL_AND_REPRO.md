# Stage 4 待执行试用与独立复现

**USER_TRIAL_BLOCKED。** 用户于 2026-10-12 明确本轮仍无独立操作者。此文是可执行说明和空表，不是反馈、已完成的复现或比赛接收记录。先前开发核查者的测试不能记作队外用户。

## 固定版本和环境

源码基线 commit `3ed5d32bca171f901072edac7bf479875b5c5413` 加保全的 stage3.patch。入口 SHA-256 必须为 `ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b`，bundle BLAKE3 必须为 `1dc41555dee5c43f11690dcea7d0e937e05e95fdf08f0bb7e426c2c2a551f998`。现有改动未提交，不能只记 Git HEAD 便称版本完整。

本机源保全在 `F:/CodexWorkspace/05-Backups/RippleStage4-20261012-1617`，独立副本在 `F:/CodexWorkspace/Projects/RippleStage4-20261012`。保全包只含补丁、经核对的测试/文档和摘要，不含凭据/旧运行数据；不要把整个本机目录打包给其他人。

本轮从四份独立 SDK Git 副本重新构建，使用本机已有 Cargo registry 缓存。不是全新 Windows 安装，也没有验证在线首次下载所有 Rust 依赖。Windows 官方 RC2/RC6 使用发行包解包副本，未运行系统安装器。具体源码/宿主 SHA 见 `evidence/dependency-and-host-pins.json`。

独立操作者须获得有权访问的源码基线及补丁，在自己的新目录 `git clone --no-hardlinks --no-checkout <可访问的源码仓库> <新目录>`，切至上述完整 commit 的新分支；先 `git apply --check <stage3.patch>`，再应用。核对入口和 bundle 摘要。不要复制 .env、Kernel core、Provider 数据库、活动、会话或 peer。当前基线未公开发布；不能假定 GitHub 上能取到本地开发 commit。源码可访问性是独立复现前提。

SDK 来源固定为 OctoSense-org 的四仓库：Makepad `32d6415fb7476345ad36ee4f98d6f844d1f07fd2`，Octoscript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`，Octoscript-Makepad `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`，OctoSense-App-Hub `95e4831afca7227b640f075b252c04355bb63865`。目录对应 `phase1/toolchain/{makepad,octoscript,octoscript-makepad,OctoSense-App-Hub}`。Rust 1.97.1，Python 3.10.8。本轮 `stage4/setup.py` 使用本机源码和发行资产，只适合本机核查者，不伪装成通用安装器。

## 原生安装及 Provider

1. 在新副本执行 `stage4/new_run.ps1 -Name p4-user-<唯一编号>`。它创建仅当前用户、SYSTEM、Administrators 可访问的空运行根；不复制 Provider。历史目录及权限保持不动。
2. 设置 `RIPPLE_TEST_RUN` 为该名称、`RIPPLE_STAGE4_HOST` 为 `rc2` 或 `rc6`，执行 `python -B stage4/host.py prepare` 和 `python -B stage4/host.py start <唯一标签>`。这只使用已授权的本地签名测试目录和进程测试锚，不是公开 Hub 发行。
3. 打开新宿主的 App Hub，核对 Ripple 安装权限，安装并打开。RC2 冷 Hub 显示 Unavailable 时，先正常安装并打开普通 bootstrap Card，关闭它和 Hub，再开 Hub；不得删除 requires 或关闭校验。RC6 本机实测无需此预热。安装确认后需滚回详情顶部才能看到 Open。
4. 新宿主当前没有 Provider。完整模型流程开始前，由操作者在该隔离宿主的官方 AI Providers 界面自行配置有权使用的 Provider 并授权；不能在聊天、截图或记录中填写 Key。**本轮没有验证此新配置步骤，也没有新的真实模型成功记录。** 若缺 Provider，应明确 FAILED、无批准按钮、无活动改期。
5. 首次 App Hub/Ripple Agent 可能分别请求授权。授权不会自动把已失败任务变成成功；明确重试并记录次数。只对这个新宿主操作，勿改其他宿主默认配置。

## 真实用户任务

不需要个人日历权限。Ripple 仅修改手工输入的一条本地活动。界面时间为 UTC+8，地点时区不自动换算。经纬度会发给 Open-Meteo；授权后活动事实、天气和候选会发给选择的模型 Provider。只使用本人愿意分享的最少信息。

1. 在看建议前，非开发用户记录自己确实可能参加的户外计划、当前难题、时间/地点/时长、真实可用时间和偏好。记录者不代填，也不为制造差异改变约束。
2. 输入未来七天内的活动，时长 15–240 分钟，保存并核对。点击 Analyze with Agent。没有雨就记录 LIVE NO_CHANGE；失败也原样记录，不为展示改用虚构雨天。
3. 使用实际返回的同一候选集合，A 取最早有效候选，B 取现有 Agent 的候选。两者对照必须固定活动、天气版本和约束；不得重新取天气或换候选。若 A=B，如实记录相同。
4. 当前产品没有偏好/可用窗口输入；用户约束仅用于评价两方案是否可用，不能声称模型理解了未传入的信息。不得临时修改提示词来制造 AI 优势。
5. 用户自行批准或拒绝。核对实际保存记录、执行收据、独立回读，再仅改标题保存、关闭重开。拒绝应保留原活动。记录实际耗时、错误、重试、理解困难和原话。
6. 若审计容量不足，不能重新拼造缺失的工具记录；结束该次，另开全新测试环境继续。fixture 只用于另列的确定性回归，不计入真实用户/实时天气试用。

| 字段 | 真实操作者填写 |
|---|---|
| 日期、操作者代号、未参与开发声明、记录同意 | 未填写 |
| 源码/补丁 SHA、bundle 摘要、宿主与平台 | 未填写 |
| 原本难题、真实活动事实、UTC+8 换算 | 未填写 |
| 看建议前的可用时间/偏好及原话 | 未填写 |
| Provider 名称、天气 LIVE/FIXTURE、天气/候选证据引用 | 未填写，不填 Key |
| A/B 候选、是否合法、是否本人可用、相同或不同 | 未填写 |
| 用户接受/拒绝及理由；是否仍有规则未表达的需求 | 未填写 |
| 完整耗时、模型等待、错误、授权和重试 | 未填写 |
| 审批、实际记录、收据、回读、重开证据 | 未填写 |
| 是否理解只改 Ripple 本地活动；真实困难和逐字反馈 | 未填写 |
| 独立复现者按说明完成/卡住的具体步骤 | 未填写 |

## SDK 回归与验收门槛

给 `MAKEPAD=headless`、`RIPPLE_TEST_ROOT=<新工作副本>`、`RIPPLE_TEST_EVIDENCE=<全新空证据目录>`、`CARGO_TARGET_DIR=<新工作副本内独立 target>`、`RUST_BACKTRACE=full`，运行：

```powershell
cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1 --nocapture
```

依赖缓存未准备时 offline 会失败，应记录而不是升级依赖或修改 lock。SDK 用 fixture 天气与模型回复，不能计作真实模型成功。本轮最多三轮用于有界复现历史异常，不能把重复次数变成用户成功率。

独立验收要求实际的新 Provider 调用、正常与失败闭环、原始用户反馈及固定版本证据；本轮仍缺这些独立记录。冻结后的试用不能冒充 10/9 前交付。只有真实用户证明确有约束/偏好痛点，才重新评估最小增强；否则停止功能开发并重新审视 Agent 定位。
