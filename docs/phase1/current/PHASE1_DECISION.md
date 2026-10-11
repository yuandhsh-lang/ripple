# 第一阶段决策（最新补充）

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

**最终状态 BLOCKED。** 真实只读核心闭环和应用回答保存已验证；完整验收没有 PASS。第二阶段、第三阶段功能开发不能开始。当前阻断已不是 Provider 或用户许可，而是普通冷启动能力发现/安装，以及剩余未验证边界。

| 问题 | 实证结论 |
|---|---|
| Windows 官方宿主支持目标 Agent 吗？ | RC2 在正常许可、保存的 Provider 和 Card/Hub 特殊启动顺序下，真实支持应用 Agent 和 Splash 工具；干净 App Hub 直接安装未通过 |
| 真实模型运行了吗？ | 是。DeepSeek V4 Flash 实际生成回答，Kernel 有独立 session/turn/tool/final/completed 记录；不是仅 Test connection |
| 模型实际调用 Splash 吗？ | 是。context.read 有真实 call_id、script-tool token、实际 fs.read 和返回、模型回答。仅一个只读工具；slots.search 未实现 |
| 下一阶段首选接口？ | 官方 app Agent + octos.session.open/turn.start/history + tools.json + script-tools-v1 + app_tool/mod.app_tools。实际路径已验证，无需独立 AI 后端 |
| 必须更换宿主/系统吗？ | 合成日程只读模型闭环无需更换系统；完整安装复现仍需要官方修复/支持路径。其他平台解决缓存问题未验证，不推荐未经验证迁移 |
| 当前技术阻断？ | 普通干净 RC2 App Hub 显示 Unavailable；启动 Card 再刷新仍有 Store 能力快照，重开 Hub 才成功。非法参数、服务超时、重复/迟到边界未验证 |
| 第二阶段可安全开始吗？ | 不可。按用户强制门槛停在第一阶段。候选搜索、结构化建议校验、旧提案失效、重规划和审批对接均不存在 |
| 冻结与发布风险？ | 是，10/9 后的新 Agent 能力只能称实验；当前正式 v0.1.0、tag、提交和 App Hub Issue 保留，没有补交或覆盖 |

当前源码 `phase1/probe-quota/bundle` / 0.1.3-phase1，全部业务读取与原探针一致。0.1.1、0.1.2 及失败材料保留。0.1.3 调整实验 storage.max_bytes 为 1 MiB，真实解决含 Kernel 工作子目录的 64 KiB 超额问题；有界回答按源码 len()>8192 上界限制；长度单位与 UTF-8 字节长度未独立测量。官方工具链未改。

关键证据：本目录 PHASE1_EVIDENCE.json 和 PHASE1_REAL_AGENT_VALIDATION.md；`phase1/evidence/phase2-gate-20261010-1027/continuation-correlation.json` 包含实际结果、回答、逐字段比较、空数据、关闭应用、非法记录、无 Provider、拒绝许可和恢复记录。

六关卡未来受到这些限制：真实天气必须检查地点/时区/覆盖/有效期；合成日程不能冒充个人日历；原审批与独立读回未接 Agent，需要保持版本约束；自然语言理解的模型时间换算实际出现错误；候选必须由确定性 slots.search 产生并校验；反馈重规划必须加入任务代次和旧提案失效，重复/迟到/超时仍要实测。Windows RC2 device_calendar 的实际 discovery 为 supported=false；未来个人日历写入需要另行验证正式连接接口与宿主支持，Agent 读取许可不能替代一次写入批准。

目前无须用户重新输入模型凭据或再次允许同一只读范围。最小后续依赖是官方兼容宿主的可复现安装路径；禁止自行修改官方门禁解决。剩余安全边界在该路径确定后继续真实验收，并保留原文件、Provider 和历史状态。
