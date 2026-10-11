# 第一阶段最新前置复测

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

**完整验收 BLOCKED。** 用户许可和 Provider 已确认，当前 0.1.3-phase1 的真实模型 → context.read → Splash 实际状态 → 工具返回 → 模型回答 → 应用显示已验证。第一阶段完整条件仍未满足，第二阶段业务开发未开始，第三阶段不能开始。

真实模型 call_id `call_00_A8Tt7bMEXhDTDBbbCBu28819`，turn_id `7df15e9a-dec4-4be3-9092-443e778692a1`，Splash token script-tool-2；有数据、空数据、关闭应用错误、恢复 Provider 后 revision 2 和非法记录错误均有真实模型记录。已许可但无 Provider 的请求诚实返回 profile_unresolved；原拒绝许可测试零工具调用、日程未变。

原 0.1.1/0.1.2 保存失败已查明：应用沙盒包含 Kernel 工作子目录，递归超出声明 64 KiB；0.1.3 声明 1 MiB 后真实回答保存成功。所有版本及失败记录保留。新普通无测试参数的 RC2 冷启动仍在 App Hub 显示 Unavailable，需先启动 Card 并重开 Hub 才能安装；没有修改官方门禁。非法参数、超时、重复和迟到边界继续明确未验证。

最新完整报告在 [current/PHASE1_REAL_AGENT_VALIDATION.md](current/PHASE1_REAL_AGENT_VALIDATION.md)、[current/PHASE1_DECISION.md](current/PHASE1_DECISION.md)、[current/PHASE1_EVIDENCE.json](current/PHASE1_EVIDENCE.json)。第二阶段文件在 ../phase2/，原始证据在 phase1/evidence/phase2-gate-20261010-1027/。本文旧版已在 ../phase2/history/gate-before-consent-continuation.zip 归档并核对哈希，根目录 PHASE1 历史报告未覆盖。

原仓库、原应用状态与 Git 记录复核一致。模型配置继续保留，目前无须用户重新输入凭据或再次许可。
