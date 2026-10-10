# Ripple 第一阶段交付记录

**最终状态：PASS（业务闭环；官方 RC2 使用已知预热流程，干净冷启动未通过）。**

本地项目：`F:\CodexWorkspace\Projects\RipplePhase1-20261010`；分支 `dev/phase1-complete-20261011`；版本 `0.2.2-stage1`。基线 HEAD 为 `86b768adcd7823cc1efd6771612160b464b25378`。交付后的本地提交与源码哈希记录在 `evidence/code-version.json`，当前验收记录在 `evidence/acceptance-current.json`。没有推送或发布。

## 代码与旧成果的关系

原始仓库 `F:\桌面\01 项目开发\黑客松\Ripple` 的 main、v0.1.0 冻结包和旧数据均保留。根目录 `bundle/` 是正式参赛冻结路径，`src/` 是旧 React 原型；上一轮 `phase1/probe-authority-timely/bundle/` 提供已验证 UTC/存储修复，`phase2/readonly-prep/bundle/` 提供只读双工具搜索。新业务运行入口为 `stage1/bundle/main.splash`；旧实验包没有被替换或删除。完整保全核对见 `evidence/preservation-after.json`。

新增 `stage1/bundle/` 中的 main.splash、manifest.json、tools.json、AGENT.md、listing.json、PRIVACY.md、原有图标副本及三张新版真实截图；新增 stage1 的 .gitignore、verify.py、acceptance.py、本报告；新增 `phase1/business-harness/` 的 .gitignore、Cargo.toml、Cargo.lock、src/lib.rs、time-vectors.json。未删除旧文件，未修改 Rust 宿主。根 .gitignore 的原有未提交修改没有纳入本次提交。

复用最新 UTC 整数算法、降雨阈值/逐小时覆盖、只读候选搜索与实际 App Tool ABI，并将持续时间扩展为用户输入的 15–240 分钟。沿用审批、唯一写入口与独立回读机制。新增稳定活动 ID/版本、真实输入与持久化、模型选择校验、一次重规划。仅移除了新测试副本中未引用的 submit 辅助函数；旧回归和历史实现全部保留。

工具声明在 tools.json：`implemented_by: app`、`risk: read`、`private_data: true`；manifest 要求 `script-tools-v1`。正式调用路径为 `octos.session.open → octos.turn.start → app_tool(name,call_id) → mod.app_tools.request/active/complete/fail`。两工具实现分别为 main.splash 中的 app_tool（context）与 slots_tool/candidate_search（slots）。真实模型最终 JSON 通过官方 turn 返回的 `data.text` 交接，引用工具产生的 task/read/search/candidate ID；程序校验后只在内存准备审批，工具不能修改日程。无需新增第三工具。

## 当前版本真实验收

官方 Windows Desktop RC2，Kernel `2.0.3-rc.13`，实际 Provider/model 为 `deepseek/deepseek-v4-flash`。活动通过正式输入控件录入，使用验收人员输入的演示标题和坐标；没有读取个人或外部日历。天气全部为 LIVE Open-Meteo，未将 FIXTURE 数据用于以下真实模型验证。

| 检查 | 结果与当前证据（均位于 evidence/） |
|---|---|
| 输入、保存、读取 | v2-user-saved-state.json；稳定 ID `ripple-1791653059.9615583` |
| 无降雨冲突 | v2-no-change-final-kernel.json：真实 context.read，模型 NO_CHANGE，无改期 |
| 双工具规划与拒绝 | v2-real-pending-decline-kernel.json：turn `72553412-5d5b-44f5-9e31-e65bedd06302` 两工具均 ok；v2-declined.png 与 restart-and-decline-comparison.json 证明拒绝不写 |
| 活动变更使旧审批失效 | v2-before-stale-edit-kernel.json、v2-stale-user-edit.png：同 ID revision 2→3，旧卡 STALE |
| 一次真实重新规划 | v2-replan-pending-kernel.json：turn `9cb3d3f2-77a7-4042-a9ab-76c546f73aad`，两个工具均 ok；v2-replan-pending.png 新审批 |
| 批准、实际写入、独立读取 | v2-independent-external-readback.json、v2-completed-final.png：expected==actual，同 ID revision 3→4；原 UTC+8 10月15日06:00–07:00 改为10月11日01:30–02:30，标题/地点/持续时间保持 |
| 关闭重开、重启保持一致 | v2-reopened.png、v2-restart-readback.png、restart-and-decline-comparison.json，活动文件 SHA256 均一致 |
| 无 Provider 不假成功 | v2-no-provider-scrolled.png、no-provider-comparison.json：独立空 Kernel profile 返回 profile_unresolved，UI FAILED、日程不变；没有更改现有凭据 |

模型选择 task `ripple-task-1791653215.6641736-5`、read_token `script-tool-7`、search_id/candidate_id 可从 Kernel assistant_persisted、应用工具返回、审批快照一路关联到最终读回记录。UI 的 COMPLETED 只发生于独立磁盘读取一致后。仅修改 Ripple 自己的活动，没有外部日历同步声明。

## 自动检查与未验证项

- **当前 SDK ABI + FIXTURE（非真实模型）**：`vm-delivery.log`，1 个综合测试通过；`vm-delivery/business-abi-results.json` 验证 18 项保护，包括错误日期/JSON schema/伪造候选、拒绝、版本陈旧、天气变化/过期、提案过期、取消迟到、重复批准/执行、无天气/无候选、一次重规划及20分钟总有效期。`vm-delivery/current-time-vectors.json`：当前 Splash 代码与独立 Python datetime 的90个 UTC/UTC+8样本全部一致。
- **旧实现回归（不替代新版证据）**：legacy-vm.log，3项通过。React 项目自身5文件63测试通过（react-owned-tests.log）；lint/typecheck/build 均退出0（react-checks.json与对应日志）。未限定目录的 npm test 失败，原因是扫描到未追踪官方源码/工具链测试中的 CRLF 正则解析错误；失败日志保留，未把全目录测试写成通过。
- **交付包静态门禁**：delivery-check.json passed=true；开发包未签名警告如实保留。真实运行使用此前本地签名安装包，核心 main/tools/AGENT 三文件哈希与交付源码完全一致；运行后仅更新 listing、真实截图、当前隐私说明及 manifest 摘要，这些包装修改通过最新门禁，不冒充另一次模型运行。
- 初期 Splash/天气 await 修复、错误 catalog 缓存证书、错误 CLI gate 命令和无默认 Rust 环境等开发失败记录均保留，最终对应检查已纠正通过。`v2-restart-direct-ripple` 实际打开的是 bootstrap，因此仅作为预热记录，不作为直接冷启动证据。
- **NOT TESTED**：Provider 传输网络超时、真实 OS 写入故障注入、修复源码宿主编译与冷启动。应用90秒 deadline 不替代 Provider 网络超时。官方固定 SDK 的 `.sources/makepad/code_editor/Cargo.toml` 缺失阻断仍是宿主源码构建限制；未重构官方 Kernel，也未宣称 dedd14a 修复已生效。

## 运行、限额与回滚

交付包仅用于本地审查，未覆盖赛事提交。宿主需已有 DeepSeek Provider、App Tool 私有数据权限和官方 RC2 已知预热流程。listing 的隐私 URL 为明确的 example.invalid 本地测试占位，当前规则在 bundle/PRIVACY.md；公开发行需人工批准并提供真实当前隐私地址。

天气快照、选择和执行收据各只保留当前份，诊断日志约24 KB封顶，天气10分钟有效、最多3候选、一次重规划、整次流程20分钟。当前真实沙箱148,616字节，限额1,048,576字节；增长记录见各 v2-*-state.json。宿主会话存储仍增长，没有通过清空日程或证据控制容量。

复现自动回归：使用现有1.97.1 Rust与已准备的 phase1/toolchain；设置 RIPPLE_TEST_ROOT 为项目目录、RIPPLE_TEST_EVIDENCE 为新建的空证据目录，执行 `cargo test --offline --locked --manifest-path phase1/business-harness/Cargo.toml -- --nocapture`。正式 RC2 的本地安装/控件/快照辅助在 verify.py；acceptance.py 只核对已捕获记录，不能替代实时运行。

回滚开发代码可在独立分支 revert 本次本地提交，或回到原冻结包使用独立沙箱；不用 reset/clean，不清空新活动，也不让旧schema包覆盖新版活动数据。第二阶段仅需解决宿主干净冷启动/固定SDK构建、Kernel会话留存与配额、Provider网络超时及真实写入故障专项。第一阶段核心闭环已真实完成，无待重启验证。
