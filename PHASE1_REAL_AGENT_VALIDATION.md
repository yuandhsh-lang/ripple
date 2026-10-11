# Ripple 第一阶段真实 Agent 技术验证

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](docs/experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

验收日期：2026-10-10（Asia/Shanghai）。本次结论：**BLOCKED**。

已实际运行官方 Windows RC2，完成隔离、本地签名目录安装、完整实验 Splash 启动、运行能力查询和未授权拒绝验证。尚未取得真实模型会话、模型选择工具、Splash 工具执行及结果回传证据，因此不能宣布阶段一通过。用户回复了“已通过 Test connection”，但本次隔离 Provider 首页仍显示 `Connect your first model`，其 Kernel 配置目录尚无文件；“连接测试成功”和“这个隔离配置已保存且供 Agent 使用”必须分别验证。已请求用户在该窗口保存模型，未读取或搬运任何凭据。

## 1. 基线与保护

真实原仓库：`F:\桌面\01 项目开发\黑客松\Ripple`，remote 为 `https://github.com/yuandhsh-lang/ripple.git`。主分支 HEAD 与 `v0.1.0^{}` 均为 `86b768adcd7823cc1efd6771612160b464b25378`。tag 对象 `c987eaa05d3b60308ee5398c814433a5e0192790` 完整保留。`qualifying-2026-10-04` 也未改变。

原始 `bundle/main.splash` SHA-256：`9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`。原 manifest 的 Agent 缺省，即无 Agent；只有 storage/net 与 Open-Meteo。公开 [Issue #94](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/94) 的源码、版本和评分信息已只读核对，未编辑 Issue。

开始时唯一未跟踪文件为 `submission/video/Ripple-OctoScript-Demo-v0.1.0-final.mp4`。前后比较：95 个跟踪/未跟踪文件的哈希、3 个原应用状态文件哈希、原 build 文件清单、HEAD、两个 tag、Git 状态、暂存和工作区 diff 全部一致。见 `phase1/evidence/original-before.json`、`original-after.json`、`original-integrity-comparison.json`。Git 新增了本实验 worktree 的正常管理元数据，未重写历史。

隔离 worktree：`F:\CodexWorkspace\Projects\RipplePhase1-20261010`，分支 `experiment/phase1-real-agent-20261010`，从上述固定提交创建。实验源码只在 `phase1/probe/bundle/`。原根 `bundle/` 和原业务代码未修改。数据分离如下：

| 用途 | 本 worktree 下的目录 |
|---|---|
| 用户配置模型的隔离 Shell | `phase1/runtime/shell-home`、`shell-apps`、`kernel-core` |
| 无 Provider 的安全测试 Shell | `phase1/runtime/lab-no-provider-bootstrap-home`、`lab-no-provider-bootstrap-apps`、`no-provider-core` |
| 普通 card-host 基线/布局预览 | `phase1/runtime/baseline-apps`、`preview-apps` |
| 本地测试目录与签名包 | `phase1/runtime/lab-mirror-bootstrap-v2`、`lab-probe-bootstrap-v2` |

实验沿用 `ripple` id，但使用完全不同的 Shell/应用数据目录。用于正常初始化 Card 模块的无 Agent 基线副本另用 `phase1.bootstrap` id；它没有工具，不能作为 Ripple Agent 集成证据。

## 2. 官方来源与版本

完整下载 URL、文件 SHA-256 与 commit 见 `phase1/sources/INDEX.json`、`TARGETED-INDEX.json`、`PINNED-INDEX.json`。核对了 AGENTS、QUICKSTART、AI-SERVICES、HOST-API-V1、CAPABILITIES、SUBMITTING、PUBLISHING、Agent 配置、工具声明、脚本执行、桌面发布与赛事文件。路径猜测产生的 404 留在下载索引中，实际文件按索引定位。

| 官方项目 | 本次核对的最新快照 commit |
|---|---|
| [OctoSense](https://github.com/OctoSense-org/OctoSense) | `40ca21da68cc05ae930931adcfcf6d382d49ec26` |
| [App Flow](https://github.com/OctoSense-org/OctoSense-App-Flow) | `e590035825beb42d1c5081025d4f08b1aa21e9f0` |
| [App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) | `7b36c8afc2e4bad9dfa5d77692b6fd453f0b9785` |
| [比赛仓库](https://github.com/gosimfoundation/hackathon-agenticapp26) | `600c32305f0e70261c91f01d328af73c0971e756` |

实际运行 [desktop-v0.1.0-rc.2](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.2)，产品源码 `4ccf8e068399b1da139771a9ed94cef05fa6ae60`，app-contract 1.10.0。配套 App Hub 固定源码 `95e4831afca7227b640f075b252c04355bb63865`；Makepad `32d6415fb7476345ad36ee4f98d6f844d1f07fd2`；OctoScript-Makepad `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`；OctoScript `2e37d9e657a246f16718d9a475e167ccd2d5b5fa`。最新 main 的 contract 1.11.0 变化不等于 RC2 已具有全部新行为。

原目录已有旧 hub/card-host，先复用检查；没有发现匹配 RC2 的正式 Shell 安装。旧 hub 在 Windows 拒绝 `assets\\icon.svg`，其 WSL 检查随后因跨平台旧 stamp 摘要不一致拒绝，均保留真实失败。改用 RC2 固定版本官方 hub 后，基线与实验结构检查均成功；没有更改官方准入代码。

## 3. 实际环境与宿主

Windows 11 家庭版中文版，NT `10.0.26200`，64 位；AMD Ryzen 5 6600H，x64。Git 2.55.0.windows.2、Python 3.10.8、Node 24.14.0、WebView2 154.0.4258.62。Rust/Cargo 默认工具链未配置，已有 `+1.97.1` 可用，未改变系统默认值。hub/card-host/octosense/octos 不在 PATH，直接使用已经核对的绝对路径。

官方 RC2 包 SHA-256：`628a68a0d9e5fa615ca01d3a6e3ff2bbd2ccd02cf71ec6acbd9e28a652c58e00`，与官方 release digest 和 SHA256SUMS 一致。用户明确批准“批准隔离运行 RC2”。使用本机已有 7z 静态解包；未执行 NSIS 安装器、未提权、未改注册表或系统配置。Shell exe SHA-256：`7d8027bc64618948dcef26b911978b444490034c49e010d6a87dd3d989cd55d0`。

Kernel 原包及 receipt 校验一致，SHA-256：`5ffdbf58d86ab778d1436db4ddcea3621d67ec833c3959e75136b1323a6e02c0`。实际执行 `octos-kernel.exe --version` 得到 `octos 2.0.3-rc.13 (b0759a5 2026-10-09)`。Shell 日志报告 Kernel service ready、starts on first use；尚未观察到真实 Agent Kernel 会话或运行中的 Kernel 服务进程。二进制版本检查不是模型连接测试。

第一次启动把 test-action 写成 `launch:ai-providers`，宿主报告 unknown；改为官方 `launch-ai-providers`。此外 `MAKEPAD_HIDE_WINDOWS=0` 仍隐藏窗口，源码按变量是否存在判断；随后彻底移除该变量，实际显示 Provider 窗口。失败和修正保留在日志中。

## 4. 最小实验与正常安装路径

实验 version `0.1.1-phase1`，未发布。`manifest.json` 声明应用 Agent、`requires: ["script-tools-v1"]`、必要 storage/runtime/octos 会话权限；`tools.json` 只有 `ripple.context.read`，`AGENT.md` 要求读取实际数据再回答。

工具每次从自己的 `schedule.txt` 重新读取原 Ripple 六段记录格式，校验时间、时长、位置范围和 revision，仅向 Agent 返回 event_id/start/end/revision/data_source/retrieved_at。event_id 从实际时间和 revision 派生，retrieved_at 来自运行时钟。没有固定工具结果，没有日程写入工具。UI 中 Seed/Empty 是操作者合成数据准备按钮，不能被 Agent 调用。工具只追加关联审计，不改日程。

普通旧 card-host 仅用于布局截图准备：预览副本移除了不支持的 requires/runtime；完整实验未移除。这些截图和启动结果明确排除在 Agent 验收之外。真实 RC2 完整实验截图为 `probe-first-start-consent.png`（当时尚未触发许可）、`probe-agent-first-request.png` 和 `probe-agent-denied.png`。签名包的原 listing 截图来自相同实验代码的布局预览，不能作为 RC2 或真实 Agent 证据。

使用官方允许的本地 rehearsal 和临时信任目录，throwaway 私钥在仓库外临时目录中产生，签名结束即删除；只保留公钥、签名、官方门禁报告及本地目录。没有伪造 GitHub attestation、官方 publisher 身份或公共准入，也没有向公共 Hub 发布。

实际发现并解决的启动顺序问题：

1. 干净 Shell 先打开 App Hub，实验显示 `Unavailable`。
2. 正常安装并打开无 Agent 基线副本，CardModule 注册 `app_tools.dispatch@1`；刷新 UI 后显示 Get。
3. 安装仍被拒绝：`app ripple needs a host implementing app_tools.dispatch@1`。原因是 App Hub Store 在创建时保存了旧能力快照。
4. 保留 Card 副本运行，正常关闭并重新打开 App Hub，再安装完整实验，成功安装和启动。

来源定位：固定 App Hub 的 `crates/appstore/src/cardapp.rs` 中 CardModule::register；`crates/app-hub-app/src/catalog.rs` 创建 Store 时调用 with_host_api_versions，展示状态又查询当前能力。此修复只调整正常 UI 启动顺序，不修改宿主、缓存、信任或检查标准。截图、拒绝文本及安装记录见 evidence。

## 5. 真实验收结果

| 测试 | 本次实际结果 | 证据与界限 |
|---|---|---|
| A：Shell/Kernel/Provider/Agent | **BLOCKED** | RC2 启动、Kernel 字节与版本确认；Provider 未确认保存；会话被许可门禁拒绝。没有模型响应。 |
| B：真实模型选择并调用工具 | **BLOCKED** | session_id=null，tool_call_id=null，没有 RECEIVED/RETURNED 工具日志。绝不将 ABI 或安装成功计为 PASS。 |
| C1：未允许 Agent | **PASS（仅此子项）** | 实際首请求返回 `SESSION ERROR: Waiting for the person to allow this app's agent (OctoSense asks the first time)`；正常选择 Don't allow，consent.json 中 ripple.allowed=false；重试同样拒绝，日程内容相同。 |
| C2：Provider 未配置时 Agent 行为 | **未验证** | 独立无 Provider 目录及空 Provider 首页已观察；会话先被 consent 门禁拦住，尚未走到 Provider 错误分支。 |
| C3：工具执行失败 | **未验证** | 尚无真实工具调用，不能把代码中的 fail 分支当运行结果。 |
| C4：应用未运行时调用 | **未验证** | 未发生真实模型调用；源码规定绑定到运行中的应用，不作为实测结论。 |
| C5：无日程数据 | **未验证（Agent 层）** | 空状态 UI 实际出现；未获模型读取空 events 的证据。 |
| C6：非法参数 | **未验证** | 已声明 input_schema additionalProperties=false，未进行真实调用拒绝测试。 |
| C7：模型服务超时 | **未验证** | 无实际模型服务请求；没有用取消或工具超时冒充模型超时。 |
| C8：重复请求、迟到结果 | **未验证** | 源码使用 active(call_id)，但未取得真实重复/迟到调用证据。 |
| D：原版无损、运行能力 | **PASS（限定已执行检查）** | 文件/状态/Git 对比全部一致；固定版复制构建、真实 card-host 启动及 Open-Meteo 167 小时结果；相同原 Splash 源码在 RC2 的独立 bootstrap 沙盒也真实启动。未向原正式数据目录注入测试。 |

运行时实际 `runtime.list`：platform=windows，包含 app_tools.dispatch@1 与 app_policy.device_consent@1。`runtime.describe("app_tools.dispatch")` 返回 implemented=true、supported=true、kind=runtime-abi、callable_via_host_request=false。它是 `mod.app_tools` ABI，不应当直接作为 host.request 的业务方法调用。RC2 runtime.list 没有列出 octos 会话描述；实际 octos.session.open 的 consent 错误证明服务路由存在，不能由发现列表推断其模型已配置。

安全拒绝证据：`no-provider-phase1-tool-audit.log` 两次 SESSION ERROR，日程为同一 `ripple-test-v1|1791629712|1791633312|31.23|121.47|1`。这只是合成测试记录，不是个人数据。无任何真正工具 call_id，更没有模型工具完成证明。

## 6. 构建、检查、失败与命令

完整命令参数和返回码见 baseline-commands.json、toolchain-commands.json、runtime-sources-commands.json、project-checks.json、local-mirror-commands.json、bootstrap-mirror-commands.json、bootstrap-mirror-v2-commands.json、final-local-checks.json、environment-safe.json 和各 process.json；对应可复现驱动源码保存在 phase1/*.py。UI 的 /snap、/g?raw=1、/click、/m 操作及部分只读 PowerShell/rg 检索来自本聊天工具记录，未事先启用逐条终端转录，因此不声称日志已完整逐字保存全部检索命令。

关键实际执行序列（从隔离 worktree 执行；正式目录仅被读取）：

```powershell
git -C 'F:\桌面\01 项目开发\黑客松\Ripple' status --porcelain=v2 --branch
git -C 'F:\桌面\01 项目开发\黑客松\Ripple' rev-parse HEAD
git -C 'F:\桌面\01 项目开发\黑客松\Ripple' show-ref --tags
git -C 'F:\桌面\01 项目开发\黑客松\Ripple' rev-parse 'v0.1.0^{}'
git -C 'F:\桌面\01 项目开发\黑客松\Ripple' worktree add -b experiment/phase1-real-agent-20261010 'F:\CodexWorkspace\Projects\RipplePhase1-20261010' 86b768adcd7823cc1efd6771612160b464b25378
python phase1\collect_official.py
python phase1\fetch_targeted.py
python phase1\fetch_pinned.py
python phase1\run_baseline.py
python phase1\download_rc2.py
python phase1\prepare_hub.py
python phase1\prepare_runtime_sources.py
python phase1\start_rc2.py --visible
python phase1\run_project_checks.py
python phase1\preview_probe.py
python phase1\prepare_local_mirror.py
python phase1\start_lab.py --no-provider
python phase1\prepare_bootstrap_mirror.py
python phase1\start_lab.py --no-provider --bootstrap
python phase1\final_local_checks.py
```

Provider handoff 指定的 `ProviderSwitch.ps1 -Action restore-handoff` 因文件不存在失败；只找到被禁用文件，未执行它，也未改变 Codex Provider。依赖复用用 robocopy 复制现有 node_modules 到隔离工作区，未写原目录。7z 解包命令及具体启动环境保留在脚本/证据中。

官方 hub 实际构建：在 `phase1/toolchain/OctoSense-App-Hub` 先运行 `cargo +1.97.1 build --locked --offline --release -p octosense-app-hub --bin hub`，缺少 fs2，失败；随后正常在线构建 `cargo +1.97.1 build --release -p octosense-app-hub --bin hub` 成功。最终四个工具链 checkout 的 git status 均为空，未改变锁文件或源码。

Ripple 原有 5 个测试文件共 **63/63 PASS**，lint/typecheck/build 成功。第一次无过滤 npm test 把隔离目录内新下载的官方工具链 .test.mjs 也纳入 Vitest，产生 6 个与 Ripple 无关的失败，保留 project-test.log；一次中间筛选只跑 45 个用例，不用作最终结果。最后明确列出全部 5 个 Ripple 测试文件运行，保留 project-test-ripple-all.log。没有修改测试配置来掩盖失败。

`prepare_bootstrap_mirror.py` 首次将 integrity 删除，官方 stamp 拒绝 missing field；修正为需要的空 bundle_blake3，使用全新 v2 目录，保留失败副本与命令。前两张误将 /g 返回 JSON 保存成 PNG 的文件已另存 capture-response.json，真正图片均为 /g?raw=1；不把 JSON 或空帧作为图片证据。

## 7. 规则边界与下一步

赛事 [competition-schedule.md（固定快照）](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md) 规定决赛沿用 10/9 23:59 冻结应用、源码和贡献证据，阻塞性修复需登记并由评审处理，不能增加功能/贡献得分。今天开发的 Agent 是新增实验功能，不能包装成冻结版已具有的参赛能力，也不能自行替换 App Hub v0.1.0。本实验没有提交、发布、推送、移动 tag 或联系主办方。

最小解除步骤：用户在已显示的隔离 Provider 窗口**保存**支持工具调用的模型，随后在正式宿主的 Ripple 只读 Agent 许可窗批准运行。由本 Agent 接续真实会话和 B/C 测试，不能用宿主的 Test connection 单独替代验收。主线模型与六个字段实际工具结果关联成功前，不进入第二阶段完整 Agent 产品开发。Windows 原生日历 API 的平台限制与下一阶段六关卡约束详见 PHASE1_DECISION.md。

回滚：本阶段未改正式代码/数据，无正式版代码回滚需求。停止本实验拥有的进程即可；保留 worktree 和证据。若后续需要移除实验目录，先确认模型设置是否需要保留，由用户决定；不自动删除证据、状态或原仓库。可随时以原 v0.1.0 tag 和上述哈希复核正式基线。

交付时已用各自官方 /quit 正常停止两个隐藏 card-host 和无 Provider 测试 Shell。只保留用户正在配置的可见 Provider 窗口作为人工交接，PID 37308/port 8155；见 process-cleanup.json。没有宣称这些后台进程代表持续成功运行。
