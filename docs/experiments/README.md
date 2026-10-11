# Ripple 实验源码与历史报告索引

整理日期：2026-10-12。这里保存 2026-10-10 的隔离实验源码、可复用驱动和历史结论，便于审查演进及复现。原始会话、截图、命令输出、下载快照、工具链和 Provider 数据留在本地忽略目录。历史报告中的 PASS/BLOCKED 仅对应报告注明的版本与时间，不等于本次重新验收。

当前开发应用是 [`stage1/bundle/`](../../stage1/bundle/manifest.json)，后续质量记录是 [`stage2/FINAL_QUALITY_AUDIT.md`](../../stage2/FINAL_QUALITY_AUDIT.md)。根 [`bundle/`](../../bundle/manifest.json) 是保留的 v0.1.0 交付版本；本次整理没有替换它。

## 保留的源码

| 路径 | 用途 |
| --- | --- |
| [`phase1/probe/`](../../phase1/probe/README.md) | 初始只读 Agent 实验，读取合成 schedule，不写日程 |
| `phase1/probe-repaired/`、`phase1/probe-quota/` | 保存回执与存储配额问题的版本对照 |
| `phase1/probe-authority/`、`phase1/probe-authority-timely/` | 程序时间权威、任务代次及模型回执校验的版本对照 |
| [`phase1/authority/`](../../phase1/authority/time_and_guard.splash) | 组合进探针的时间校验与只读候选搜索源码片段 |
| [`phase2/readonly-prep/`](../../phase2/readonly-prep/bundle/main.splash) | `context.read` 与 `slots.search` 的只读准备原型 |
| [`phase1/reliability-harness/`](../../phase1/reliability-harness/src/lib.rs) | 真实 SDK 队列及 Splash VM 的 schema、取消、迟到结果、时间及候选校验测试 |
| [`phase1/business-harness/`](../../phase1/business-harness/src/lib.rs) | 后续开发应用的输入、审批、写入及独立读回测试，已在先前提交中维护 |

实验包只保存代码、manifest/tools/listing 模板和图标；`screenshots/` 是本地预览证据，不随源码提交。因此这些目录不能直接作为完整发行包提交到 App Hub。结构门禁应在新本地副本中补齐明确标注来源的预览截图，再执行官方 stamp/check。不能把旧截图当作新版运行证据。

## 脚本与复现条件

[`phase1/check_sources.py`](../../phase1/check_sources.py) 只解析 Python 和实验 manifest/tools/listing，检查必需文件及只读工具约束，不导入历史驱动或启动宿主。CI 同时运行已有的 `stage2/test_isolation.py`，验证启动隔离、端口占用和 PID 检查。

[`phase1/run_project_checks.py`](../../phase1/run_project_checks.py) 从 PATH 寻找 npm，依次运行测试、集成测试、lint、类型检查和构建，每次在新的 `phase1/evidence/project-check-*` 目录保留输出。适用于按根 README 准备好 Node 依赖的工作区。

[`phase1/run_harnesses.py`](../../phase1/run_harnesses.py) 在新的 `phase1/evidence/source-check-*` 目录运行两组现有 SDK/VM 测试，串行执行，不复用应用状态或调用模型。它复用编译缓存，并将已跟踪的独立 datetime 金样本复制进新的测试目录。需要 RC2 固定官方源码、Cargo 依赖缓存及本机 C++ 链接工具；默认使用已验证过的 Rust `1.97.1`，通过 `--toolchain` 可显式指定其他已安装工具链，其他版本本次未验证。

SDK 路径由两个 harness 的 Cargo.toml 指定为 `phase1/toolchain/` 下的四个源码检出。固定版本：

| 官方源码 | commit |
| --- | --- |
| OctoSense-App-Hub | `95e4831afca7227b640f075b252c04355bb63865` |
| makepad | `32d6415fb7476345ad36ee4f98d6f844d1f07fd2` |
| Octoscript | `2e37d9e657a246f16718d9a475e167ccd2d5b5fa` |
| Octoscript-Makepad | `33dea2f1f3ad3f1346a219aa8cf6e91b31361e23` |

`collect_official.py`、`fetch_*.py`、`download_rc2.py` 用于获取公开文档及固定发行材料；输出在 `phase1/sources/`、`downloads/`，不入库。`prepare_hub.py` 与 `prepare_runtime_sources.py` 复用本地 Git 缓存准备上述 SDK。`recover_source.py` 与 `recover_build_sources.py` 保留当时对公开 Git 对象的校验及恢复流程，不是必需启动步骤。

本机来源由 [`phase1/local_paths.py`](../../phase1/local_paths.py) 定位：默认原仓库为 Git 的主工作树，可用 `RIPPLE_ORIGINAL_REPO` 指定；宿主源码缓存默认为原仓库 `.host/octo-workspace`，可用 `RIPPLE_HOST_WORKSPACE` 指定。旧跨 Linux 门禁工具可通过 `RIPPLE_LINUX_HUB` 指定，官方 OctoSense 缓存可通过 `RIPPLE_OCTOSENSE_SOURCE` 指定。设置这些变量不改 Provider、密钥或系统工具链。

其余 `prepare_*`、`start_*`、`recheck_gate`、`continue_gate`、`converge*`、`model_soak`、`native_faults` 和旧 `final_local_checks` 是历史运行驱动。它们保留当时的固定端口、证据目录、版本与前置状态，有些在执行或导入时会操作本地目录；不能批量导入或当成无副作用测试。重复真实宿主验收应使用后续 `stage2/run.py` 的全新运行目录及隔离检查。历史 `finalize_*`、`write_evidence.py` 是一次性报告拼装器，依赖旧原始日志且包含当时结论，只保留在本地。

## 历史报告顺序

| 阶段 | 报告 | 解释 |
| --- | --- | --- |
| 初始探针 | [验证](../../PHASE1_REAL_AGENT_VALIDATION.md)、[决策](../../PHASE1_DECISION.md) | 当时模型保存/许可尚未解除 |
| 许可和保存修复后 | [第一阶段补充](../phase1/current/PHASE1_REAL_AGENT_VALIDATION.md)、[决策](../phase1/current/PHASE1_DECISION.md)、[复测](../phase1/PHASE1_GATE_RECHECK.md) | `current` 是历史目录名 |
| 第二阶段前置 | [验收](../phase2/PHASE2_AGENT_WORKFLOW_VALIDATION.md)、[架构](../phase2/PHASE2_ARCHITECTURE.md)、[风险](../phase2/PHASE2_RISKS.md) | 描述更早的只读版本，不能当作后续开发包的现状 |
| 时间与可靠性收敛 | [验收](../convergence/PHASE1_CONVERGENCE_VALIDATION.md)、[阻断](../convergence/PHASE1_REMAINING_BLOCKERS.md)、[候选准备](../convergence/PHASE2_READONLY_PREPARATION.md) | 区分真实模型、协议注入和确定性 fixture |
| 后续开发版 | [Stage 1](../../stage1/REPORT.md)、[Stage 2](../../stage2/REPORT.md)、[质量审计](../../stage2/FINAL_QUALITY_AUDIT.md) | 对应已提交的开发应用和后续稳定性修复 |

报告提到的 JSON、签名镜像、会话、截图及哈希原始材料只在创建它们的本机目录中存在。获取源码不会获取那些数据，也不会配置模型。复现新的模型会话、验证宿主普通冷安装、长期配额及外部服务超时需要另外执行；源码检查和 fixture 测试不能代替这些实测。

本次整理的实际检查结果见 [2026-10-12 整理验收](CURATION_2026-10-12.md)。撤回整理可 revert 整理提交；本地原始文件副本保留在忽略的 `phase1/evidence/curation-original-20261012.zip`。撤回合并前还应检查工作树，使用 Git revert 保留历史，避免清空实验运行数据。
