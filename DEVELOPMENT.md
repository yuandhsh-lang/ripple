# Ripple 当前本机开发入口

唯一正式仓库：`F:\桌面\01 项目开发\黑客松\Ripple`，开发分支 `main`。2026-10-13 已从受保护的冻结分支切换到此前合并的开发提交；没有复制另一个仓库覆盖原 `.git`。

开发应用是 `stage1/bundle/`，入口 `main.splash`，版本 `0.6.2-rc.2`。根 `bundle/` 仍为 v0.1.0 历史交付。React/TypeScript 的 `src/` 是保留的早期原型。不要将 React 构建成功当成原生 Agent 完整验证。

本次源码统一没有新增业务逻辑；阶段三的时间编辑同步修复已经存在于合并提交。参赛版本接收仍为 `COMPETITION_VERSION_UNVERIFIED`，本地开发提交不等于比赛已接收。

## 日常检查

所有命令先进入正式目录。检查现有依赖，避免为检查迁移而重新安装、升级或改锁文件。

```powershell
Set-Location -LiteralPath 'F:\桌面\01 项目开发\黑客松\Ripple'
git branch --show-current
git status --short
npm test
npm run test:integration
npm run lint
npm run typecheck
npm run build
python -B -m unittest stage2.test_isolation -v
```

## 当前原生 SDK 回归依赖

本机已在忽略目录 `phase1/toolchain/` 准备独立源码快照，不含指向 Workspace 的链接。它们是原有依赖，没有升级或修改官方源码。

| 目录 | 固定提交 |
| --- | --- |
| makepad | 32d6415fb7476345ad36ee4f98d6f844d1f07fd2 |
| octoscript | 2e37d9e657a246f16718d9a475e167ccd2d5b5fa |
| octoscript-makepad | 33dea2f1f3ad3f1346a219aa8cf6e91b31361e23 |
| OctoSense-App-Hub | 95e4831afca7227b640f075b252c04355bb63865 |

在另一台机器应从官方上游取得同样提交，按上表准备路径，并安装对应 Rust/MSVC 工具链。当前验证使用本机 Cargo registry 缓存；全新机器首次联网安装尚未验证。

每次 SDK 测试使用新的证据目录，不覆盖以前的结果：

```powershell
$runName = 'sdk-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$env:MAKEPAD = 'headless'
$env:RIPPLE_TEST_ROOT = (Get-Location).Path
$env:RIPPLE_TEST_EVIDENCE = Join-Path (Get-Location).Path ('stage4/evidence/' + $runName)
New-Item -ItemType Directory -Path $env:RIPPLE_TEST_EVIDENCE | Out-Null
$env:CARGO_TARGET_DIR = Join-Path (Get-Location).Path 'stage4/runtime/cargo-target'
$env:RUST_BACKTRACE = 'full'
cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1 --nocapture
```

此测试的天气与模型回复是 fixture。真实宿主、模型、外部天气及用户试用必须另行验收。RC2/RC6 发行资产在本机忽略目录 `stage4/runtime/`，新测试只用独立空 home/app/core；原 Provider、用户活动和历史会话仍在原位置及受限恢复包内，没有迁入日常开发状态。

## 保全与历史

目录统一审计及恢复包位于 `F:\桌面\01 项目开发\黑客松\_Recovery\Ripple-20261013-directory-unify`。其中包含私人配置和活动的原始字节，禁止上传或公开分享。Workspace 副本尚未删除，两个关联工作树仍由原仓库注册管理，不能直接删除文件夹。

历史阶段报告中的路径和 BLOCKED 结论保留原样，不能作为新一轮测试成绩。开发结果必须以桌面目录的实际源码及当轮证据为准。

## 当前 Stage 2 运行边界

可通过自然语言生成待审核草稿，然后确认、选择真实城市并保存。一个主活动及最多四项关联事实保存在原 schema 3 记录的可选 `planning` 字段；缺少该字段的旧记录保持兼容。只支持同城同日 China / Asia/Shanghai、15–240 分钟。关联记录的取消保留 ID 并设 `active=false`，不自动删除。

规划复用两个只读工具和原天气/时段校验。规则与模型看到相同候选：先最少移动项数，再偏好与优先级加权位移；仅枚举主活动及至多一项关联移动，不能声称全局最优。关联调整仅作建议；主活动改期仍走原批准、写前收据和独立读回。不运行后台监听，不同步外部日历。

原版 RC6 的隔离复现驱动为 `stage2/planning_verify.py`，复用 `stage1/verify.py`。先用 `stage4/new_run.ps1` 建立全新 `p4-stage2-*` 空环境；设置 `RIPPLE_TEST_RUN` 和仓库外 `RIPPLE_STAGE2_AUDIT`，再运行 `prepare` / `start`。测试 Provider 必须在该新环境单独授权，凭据只由测试进程环境提供，不能复制历史 Provider/core。模型的可用名称由实际 Provider 查询确认，本轮使用 `deepseek-flash`。驱动只是本地签名测试安装，不是公开发布。

SDK 严格验收除了 Cargo 返回 0，还必须检查日志没有 `"level":"error"`；保存源码哈希及失败日志。避免与原生宿主启动、shader 编译同时运行 SDK；同一源码在并发负载中的预算诊断不能用一次成功覆盖。Stage 2 原始报告在并列 `_audits/Ripple/Stage2-20261013-030438`，其中记录精确验证边界和未关闭风险。

## 当前 Stage 3 执行边界

Stage 2 的理解、工具和搜索继续复用。关联建议先显示完整变更集合，再单独批准整组（不默认授权，也不提供子集勾选）。当前规划搜索仍最多移动主活动及一项关联计划。每步复用 write_event/execute/finish_verify；同一 schedule.txt 的 revision 每项加一，execution.json 保存各步完整检查点。没有原子事务或跨进程 CAS 保证。循环交换、约束变化、陈旧天气和未知结果均停止；不自动回滚。

重启只读核对实际记录与收据，不重放后续步骤。确认部分结果后，可明确结束本次执行并重新规划批准；损坏/不匹配的原始记录保持原样。无外部日历写入或后台监听。

原版 RC6 测试继续用 stage2/planning_verify.py；Stage 3 设置 RIPPLE_STAGE3_AUDIT（并列 Stage3-* 审计目录）、RIPPLE_TEST_RUN（由 stage4/new_run.ps1 新建 p4-stage3-*），可选 RIPPLE_STAGE3_REVISION。该驱动只用于隔离本地验收，不是新开发目录。不要运行 octosense.exe --help：该 GUI 程序会忽略它并启动默认环境；只使用经过隔离检查的 start 入口。

SDK 严格检查同时拒绝任意 script time budget exceeded 文本（包括日志等级不是 error 的初始化错误）。RIPPLE_STAGE3_CASE 可在独立进程定向运行一个故障场景，默认仍运行全部；所有断言和官方预算相同。Stage 3 审计：../_audits/Ripple/Stage3-20261013-121408。

## 当前 Stage 4 变化响应

启动、保存计划后，以及“刷新天气并检查变化”会检查保存事实。计划重叠或相关时段降雨风险变化时，前台调用同一 Agent 和两个只读工具；无风险或相同语义键不重复调用。change-response.json 只保存最近语义键和处理/拒绝状态，不是计划库或审批。天气时间戳和未跨风险阈值的波动不触发新建议；审批仍严格绑定原始天气与计划字节。AI 不可用会转为明确标记的规则候选。没有后台服务或关闭后的监测。

使用原草稿/保存操作新增、修改及取消关联计划。PARTIAL/未知执行状态阻止变化分析和写入；独立核验与人工处理后才可继续。搜索、时区及活动限制不变。当前 SDK 全套包含 9 项测试（新增 stage4_change_response_and_existing_execution），仍须同时检查退出码和日志。

本轮审计与隔离驱动在 ../_audits/Ripple/Stage4-20261013-144921；RIPPLE_STAGE4_AUDIT / RIPPLE_STAGE4_REVISION / RIPPLE_TEST_RUN 可复用 stage2/planning_verify.py 的受保护启动入口。Provider 仅在隔离进程使用环境变量引用；不要复制历史 profile 或凭据。Stage 4 的运行证据、真实视频、实际退出状态及未关闭计时问题见该审计目录。原评审包未替换，本地测试签名不等于公开发行。

## Stage 5 本地交付候选

0.6.1-rc.1 是截止日后的开发候选版，未公开发布。复用原业务，仅修复忙时重复理解点击清空说明的守卫顺序。隔离驱动支持 RIPPLE_STAGE5_AUDIT / RIPPLE_STAGE5_REVISION / RIPPLE_TEST_RUN，仍必须新建 p4-stage5-*。当轮包、官方版本核对、真实模型记录、视频与复现指南保存在 ../_audits/Ripple/Stage5-20261013-154643；验收结论以 REPORT.md 为准，不由版本名推断。

## 0.6.2 产品体验候选

原生首页以自然语言为主，中文草稿逐项编辑，新计划确认后复用原保存入口与独立读回。已保存计划的时间变更仍转手动审核或原建议审批。新增展示层与草稿守卫；未增加 Agent、存储、权限或依赖。最新实际测试及限制位于 ../_audits/Ripple/Product-UX-20261013-223104。历史 SDK 间歇超限仍未关闭，不以一次成功代替稳定性结论。
