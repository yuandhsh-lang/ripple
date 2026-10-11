# Ripple Phase 1 Lab（未发布）

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../../docs/experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

源码：bundle/manifest.json、tools.json、AGENT.md、main.splash。正式 v0.1.0 bundle 位于原仓库，完整保留。本目录不是 App Hub 发布包。

唯一工具 ripple.context.read 读取实验沙盒 schedule.txt；没有写日程、HTTP、个人日历或固定模型结果。Seed/Empty 只用于操作者准备合成记录。审计中的 RETURNED 必须由真实宿主/模型记录确认，不能单独等同工具验收。

复现路线：准备与 RC2 匹配的官方 hub；只读核对发行 SHA 和 Kernel receipt；用户批准后静态解包并用独立 Shell/app/core 目录启动；用官方本地临时签名 rehearsal 安装基线 bootstrap；打开它注册 Card 运行器；重开 App Hub，安装完整 requires=script-tools-v1 的实验；在宿主保存真实 Provider 并由用户允许 Ripple Agent；Discover ABI、Seed、Ask；对照 schedule.txt、session/history、工具审计与 Kernel 实际记录。随后执行安全测试并重新核对原版哈希。

phase1/*.py 是这次隔离驱动。部分 prepare 脚本刻意拒绝已有目录，不能直接重复覆盖；本次失败副本保留，重跑应使用新目录。start_lab.py --bootstrap --visible 选择正常模型实验 profile；--no-provider 是另一个故障测试 profile，不复制配置。不得移除完整实验的 requires 来宣称 Agent 成功。

当前只验证到安装、ABI 发现及许可拒绝。真实工具分支和模型闭环未验证，见工作区根三个 PHASE1 文件。
