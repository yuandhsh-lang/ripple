# Ripple 开发与验证

唯一正式目录为本仓库，唯一原生应用入口为 `bundle/`。新版 Bundle 为 0.6.5，增加 ICS 只读占用与执行历史；实际认证发布状态以对应 Tag 的 Release 和收据为准，旧 v0.6.4 保留。`stage1/bundle/`、阶段脚本、React 原型保留历史含义，不作为新发布入口。候选范围和验收状态见 [ICS 与执行历史](docs/development/ICS_AND_HISTORY.md)。

本机准备依赖：Rust1.97.1 / MSVC；`phase1/toolchain/` 为官方固定源快照（忽略，不发布）：makepad32d6415fb7476345ad36ee4f98d6f844d1f07fd2、octoscript2e37d9e657a246f16718d9a475e167ccd2d5b5fa、octoscript-makepad33dea2f1f3ad3f1346a219aa8cf6e91b31361e23、AppHub95e4831afca7227b640f075b252c04355bb63865。此SDK测试版本与RC6实机运行分别记录。

```powershell
$env:MAKEPAD='headless'
$env:RIPPLE_TEST_ROOT=(Get-Location).Path
$env:RIPPLE_TEST_EVIDENCE='<新建的仓库外空证据目录>'
$env:CARGO_TARGET_DIR=(Join-Path (Get-Location) 'stage4/runtime/cargo-target')
cargo +1.97.1 test --locked --offline --manifest-path phase1/business-harness/Cargo.toml -- --test-threads=1 --nocapture
python -B phase1/check_sources.py
python -B -m unittest stage2.test_isolation -v
npm test
npm run test:integration
npm run lint
npm run typecheck
npm run build
```

本候选的 SDK 严格门槛同时要求退出 0、14 项测试通过且日志没有 `script time budget exceeded` 或 VM error；不与宿主启动/构建并发运行。另有 1 项显式启动诊断默认忽略，不计入这 14 项，也不能代替原严格测试。20 项 Stage3 故障子场景覆盖审批、陈旧/篡改/取消、部分执行、损坏与重启核对。测试中的故障/天气/模型注入不等于真实 Provider 验收。需要对发布 Bundle 重新运行，不沿用历史成绩。连续通过不等于历史间歇超时已归因或修复。

原生只用官方RC6独立空home/app/core，明确指定隔离目录；不要运行`octosense.exe --help`，它会启动默认数据。Provider由宿主配置，禁止复制历史会话数据库或将凭据放进源码。单一Agent、计划模型、确定性校验及唯一执行入口保持不变。

见[复现](docs/release/REPRODUCTION.md)、[发布](docs/release/RELEASING.md)、[限制](docs/release/KNOWN_LIMITATIONS.md)。源码目录之外保存完整当轮审计，公开仓库只保留经脱敏的必要记录。
