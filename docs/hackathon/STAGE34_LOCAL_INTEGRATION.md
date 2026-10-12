# Stage 3/4 本地开发集成 — 2026-10-12

本记录说明已审查的本地开发集成范围。原阶段报告保留当时的 Git 状态与测试结论，不追写或覆盖历史记录。本次本地提交、合并不代表公开发布或赛事接收。

## 业务改动

基线 commit：`3ed5d32bca171f901072edac7bf479875b5c5413`。

正式开发入口仍为 `stage1/bundle/main.splash`，manifest 版本仍为 `0.2.3-stage2`：

- 源码 SHA-256：`ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b`。
- bundle BLAKE3：`1dc41555dee5c43f11690dcea7d0e937e05e95fdf08f0bb7e426c2c2a551f998`。

业务差异只有 Stage 3 的六行时间同步修复：改期后独立回读一致，且编辑框仍是收据中的旧时间，才更新为已确认的新时间；用户另改的时间和其他未保存草稿保留。SAVE、PARTIAL、审批、执行收据和唯一写入口保持原有行为。manifest 摘要与入口字节一致，harness 增加一项 72 行专项回归。Stage 4 没有新增业务功能。

纳入 Git 的 Stage 3/4 内容仅为源文件、验证脚本、阶段报告、待执行试用说明。凭据、Kernel core、活动、会话、发行二进制、依赖副本及原始运行证据留在各自本地忽略目录。原始参赛分支 `submission/ripple-v0.1.0` 和 `v0.1.0` tag 保留在 `86b768adcd7823cc1efd6771612160b464b25378`。

## 本次集成前验证

2026-10-12 在 Stage 4 独立副本重跑：

| 检查 | 实际结果 |
|---|---|
| 当前 Splash/SDK 全套业务测试 | 5/5，退出 0；天气与模型回复为 fixture |
| 隔离守卫单元测试 | 8/8，退出 0 |
| 官方 Hub 开发结构检查 | 退出 0；保留未签名警告，只是结构预检 |
| `git diff --check` | 退出 0 |
| Stage 3/4 Python 源码 AST | 14 个文件通过 |
| 两个新运行 PowerShell 脚本语法 | 均无错误 |

业务测试命令：

```powershell
cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1 --nocapture
python -B -m unittest stage2.test_isolation -v
```

业务测试使用 `MAKEPAD=headless`、Stage 4 固定依赖、独立测试数据目录和既有隔离构建缓存。没有再次下载或升级依赖。原始命令、退出状态与输出在 Stage 4 本地 `stage4/evidence/local-integration-20261012-233350/summary.json` 和同目录日志；这些原始证据未提交 Git。

## 后续交互演示补充

Stage 4 原报告完成后，用户要求以深圳模拟活动演示，并在全新隔离宿主官方界面配置 Provider。2026-10-12 的新 RC6 演示使用相同入口 SHA、真实 DeepSeek 模型和 LIVE Open-Meteo 天气：

- 10 月 13 日 18:00–19:00 的模拟活动，天气降水 0 毫米、概率 18%，实际调用 `ripple.context.read`，返回 NO_CHANGE，原记录不变。
- 第二个模拟活动设置为预报小雨的 10 月 14 日 13:00–14:00；实际调用 `ripple.context.read` 和 `ripple.slots.search`，选择 10 月 12 日 17:30–18:30。用户已授权演示，助手点击批准；实际记录、执行收据和独立磁盘回读一致，显示 COMPLETED，revision 从 2 到 3。编辑框同步为已确认的 17:30。

演示证据位于 Stage 4 本地 `stage2/evidence/runs/p4-user-shenzhen-20261012-1707/`：`demo-live-no-change-result.json`、`demo-live-rain-after.json`、`demo-live-rain-kernel.json`、`demo-live-rain-editor-synchronized.json` 和 `demo-live-completed.png`。均为新记录，未覆盖原阶段验收。未在这轮演示中执行全部 RC2/RC6 原生异常矩阵，也没有实际重做标题保存回归；后者由集成前 SDK 测试和同 SHA 的 Stage 3 原生验收覆盖。

用户输入了模拟活动，后续分析与批准由助手演示。这不是独立用户真实需求试用，也不是独立首次复现；仍没有证明模型优于最早候选规则。提前两天的建议是否有用，尚无用户反馈。

## 历史脚本边界与未解除事项

`stage3/REPORT.md`、`stage4/REPORT.md` 和各阶段 close-out 脚本记录原阶段检查点。它们的未提交状态、零新模型调用和整体 BLOCKED 结论是当时的历史事实，不代表上述后续演示未发生。不要覆盖原始报告，或在已使用的证据目录重跑脚本。

`stage4/host.py` 是原空 Provider smoke 驱动，其 `stage4_real_model_called=False` 注记只适用于该历史测试范围，不能作为后续真实模型调用的证明。后续演示使用单独记录实际调用与工具审计的收据。`setup.py`、`finalize.py` 等脚本含本机路径和原检查点假设，并非通用安装器；仅凭本次 Git checkout 不能宣称首次安装和独立复现通过。

历史 Provider ACL、SDK `0xc0000409` 根因、长期稳定性、真实独立用户与独立复现仍未验收。参赛冻结与新版接收保持 `COMPETITION_VERSION_UNVERIFIED`。本地合并不改变这些结论，不推送、不发布、不移动参赛 tag。

## 回退

阶段三保留原 HEAD 和未提交工作区，原始参赛目录及冻结包保留原状。后续开发以新集成工作树的 `main` 为入口，避免再次从阶段三重复应用同一补丁。需要撤销集成时，在开发 `main` 上审查并使用 `git revert -m 1 <本次合并 commit>`；不使用 reset、clean 或强制覆盖，也不把开发回退应用到冻结包。
