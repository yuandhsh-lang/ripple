# 第二阶段隔离与原始元数据恢复

**最终状态：BLOCKED。** 测试隔离修复及必要回归通过，三份文件精确恢复 **1/3**；其余两份没有取得原始字节。没有开启新阶段或修改业务逻辑。

工作目录 `F:\CodexWorkspace\Projects\RipplePhase1-20261010`，分支 `dev/stage2-stability-20261011`，修复基线 `9f4557a8851259ee31b1eb9e57baf8a78b778f6b`。另建本地修复提交，最终提交号记录在 `evidence/isolation-fix-20261011/code-version.json`。未推送、未发布。

## 三份文件及可信来源

共同目录：`stage1/runtime/v2-business-apps/ripple/accounts/device/`。下表路径相对于该目录；完整绝对路径、当前大小与哈希在 [恢复记录](evidence/isolation-fix-20261011/recovery.json) 和 [测试后核对](evidence/isolation-fix-20261011/post-tests-final.json)。

| 文件 | 开始时 | 恢复及测试后 | 开发前可信 SHA-256 |
|---|---|---|---|
| `.octos/_main/context_ledgers/_main%3Aapi%3Aoctosense%23peer-ripple-22a12f906cd27b73.json` | 不存在，大小/当前SHA不可用 | **738字节，SHA等于右列** | `366567fd179461761047e3c43d178f09c5bd2b0d8746dbe59d1215dd122b0cf4` |
| `contexts/9d991bcd-p1-card-ripple-g1/.octos/_main/context_ledgers/_main%3Aapi%3Aoctosense%23peerctx-ripple-22a12f906cd27b73%2E9d991bcd-p1-card-ripple-g1.json` | 不存在，大小/当前SHA不可用 | **仍缺失**，大小/SHA不可用 | `fece11df7681271b57dfb14f31dc08448844f62de7d778e54616d03342b60361` |
| `contexts/9d991bcd-p1-card-ripple-g1/.octos/_main/sessions/_main%3Aapi%3Aoctosense%23peerctx-ripple-22a12f906cd27b73%2E9d991bcd-p1-card-ripple-g1.jsonl` | 不存在，大小/当前SHA不可用 | **仍缺失**，大小/SHA不可用 | `273d9d6c26a5feb13cbdf2431f9883e651a96d6c7c17ceba25a7b37023305b31` |

原始哈希取自上一轮开发前 `stage2/evidence/before.json`；该记录没有原始大小，不能补造。恢复来源为已有 `stage2/evidence/before-failure-tests-app-backup/accounts/device/.octos/_main/context_ledgers/` 中同名738字节文件。虽然该备份不是开发前创建，但其完整内容与独立的开发前SHA完全相符；没有重新序列化或构造内容。恢复程序仅以独占创建方式写入第一份指定文件，未覆盖邻近文件。

本次只读搜索包括：Git全部233个对象（含不可达对象，163个blob）、2,270个元数据/备份文件、4个已有ZIP备份，以及本次相关Codex历史记录中25,651个原样捕获字符串。搜索边界、备份SHA和结果见 recovery.json、transcript-search.json。两份会话专属文件未找到匹配。Windows卷影副本查询返回“初始化失败”，见 shadow-inspection.json，不能据此声称系统没有备份。仍需要包含上述两份完整原始字节的历史备份；只凭模型回复、部分工具记录或哈希无法恢复。

## 污染入口与最小修复

旧启动器只隔离 Home/App 数据，却使用共享 Kernel core；peer注册及生命周期状态仍共享。官方 broker/peer_record 源码明确保存并恢复原workspace的 cwd；purge路径依照已有peer记录工作。因此仅改Home/App目录、甚至全量复制旧core，都可能保留旧workspace引用。本次没有单文件删除审计，不能虚构此前六份文件各由哪一次删除调用移除；可以确认这一共享状态入口存在。

- `stage2/run.py` 要求显式 `RIPPLE_TEST_RUN`，为每个新验收建立 `stage2/runtime/runs/<name>` 和独立证据目录；初始化拒绝已有目录。只复制现有测试Provider配置文件，不复制core数据库、peer、workspace、Home、活动或会话历史。
- `stage1/verify.py` 在启动进程前验证新目录标记、core归属和解析后的真实路径；旧目录、外部core、缺失初始化及路径越界直接拒绝。历史启动命令不再能直接复用旧runtime。
- `vitest.config.ts` 合并现有Vite配置，保留React插件及Vitest默认规则，仅排除下载的 `phase1/toolchain/**` 和 `phase1/sources/**`；没有跳过项目测试。tsconfig.node.json同时检查新配置。
- `stage2/acceptance.py` 的剩余文件数量改为实际计数，旧证据和旧报告不改写。

实际新增：vitest.config.ts、stage2/recover_metadata.py、stage2/test_isolation.py、本报告。实际修改：stage1/verify.py、stage2/run.py、stage2/acceptance.py、tsconfig.node.json。另恢复表中第一份被Git忽略的运行元数据。未修改正式 `stage1/bundle`、冻结包或Rust宿主。

## 回归与一次真实冒烟

| 检查 | 结果与新记录 |
|---|---|
| 默认 `npm test` | **63/63，0跳过**；发现的5个测试文件与Git跟踪的项目测试集合完全一致。project-tests-final.json |
| 启动隔离回归 | **5/5**；旧目录、外部core、未初始化目录、路径越界均在创建宿主进程前拒绝。isolation-tests.log |
| 当前实际SDK + FIXTURE | **3/3**，90个UTC/UTC+8样本通过；sdk.log、sdk/current-time-vectors.json。不是模型证据 |
| 静态/构建 | lint、typecheck、build均退出0，Python编译及Git diff检查通过。typecheck-final.log同时覆盖新Vitest配置 |
| 新隔离目录的真实业务 | RC2 / Kernel2.0.3-rc.13 / DeepSeek-v4-flash / LIVE Open-Meteo，双工具→审批→写入→独立回读 **COMPLETED**；turn `e668cd5f-079f-4e84-860f-ef49f8149e3a`，同活动revision2→3。`evidence/runs/isolation-smoke-20261011/soak-2-readback.json`、approval-kernel及PNG/state |
| 实际workspace归属 | 新宿主3条持久化workspace/cwd引用全部位于本次新runtime。actual-agent-workspaces.json |
| 测试前后保全 | **3,130个保护文件**，除明确授权恢复第一份文件外，内容变化0。已恢复文件测试后SHA仍一致；另外两份仍缺失，不能算“恢复通过”。post-tests-final.json |

原Seattle测试时间的最新天气已转晴，首次真实模型正确返回NO_CHANGE；完整改期辅助脚本因期望审批而断言失败，原快照及实际工具记录保留。随后根据真实Open-Meteo选择Bergen的降雨时段，通过UI重新输入，完成上表的一轮完整冒烟。没有修改天气判断或注入FIXTURE天气。

此前5/5真实业务结果只做源码哈希及原证据关联复核，没有再跑五轮。正式main.splash仍为 `72b0ae1aaed2c5c403f817c9fd29a715123a3c55edb621121e84e61b90ef2acc`。官方RC2冷App Hub仍为Unavailable，冒烟使用已知普通Card预热；**不是干净冷启动PASS**。

## 冻结包、旧数据与执行方式

原仓库HEAD仍为 `86b768adcd7823cc1efd6771612160b464b25378`，tag、95个原文件、3个旧应用状态及历史build清单与基线一致。旧活动、历史证据、原有Provider配置内容未变。根.gitignore的既有未提交修改及历史未追踪文件没有纳入修复提交。新测试只改新runtime，结束后已关闭本次宿主。

新验收需设置 `$env:RIPPLE_TEST_RUN='新的唯一名称'`，依次执行 `python stage2/run.py init`、`prepare`、`start <日志名>`；继续沿用现有UI验收工具。init只读取已有的本地测试Provider配置。单元隔离检查为 `python -m unittest stage2/test_isolation.py -v`；项目测试直接 `npm test`。恢复程序在找到完整SHA匹配前绝不创建替代文件。

回滚本次代码可在当前分支revert本次修复提交，不使用reset/clean，不删除新证据或已精确恢复的文件。当前唯一主要阻断仍是上述两份原始内容缺失；不能宣称第二阶段PASS。
