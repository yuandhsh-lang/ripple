# Ripple 当前本机开发入口

唯一正式仓库：`F:\桌面\01 项目开发\黑客松\Ripple`，开发分支 `main`。2026-10-13 已从受保护的冻结分支切换到此前合并的开发提交；没有复制另一个仓库覆盖原 `.git`。

开发应用是 `stage1/bundle/`，入口 `main.splash`，版本 `0.4.0-stage2`。根 `bundle/` 仍为 v0.1.0 历史交付。React/TypeScript 的 `src/` 是保留的早期原型。不要将 React 构建成功当成原生 Agent 完整验证。

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
