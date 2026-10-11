# 第二阶段架构状态

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

**BLOCKED：未开始第二阶段业务开发。** 已验证官方只读 Agent 链路；候选规划、反馈重新规划与审批对接尚不存在。

实际路径为官方 RC2 Shell → 应用 peer 的 `octos.session.open` / `octos.turn.start` / `octos.session.history` → Octos Kernel → 宿主保存的 DeepSeek Provider → 模型选择声明工具 → 宿主 app_tools.dispatch → Splash `app_tool(name, call_id)` → `mod.app_tools.request/active/complete/fail` → Kernel tool_end → 模型回答 → 应用保存与显示。session、turn、模型 call_id 与 Splash token 的关联由真实记录验证，不要求两个 call_id 字符串相同。

当前实验 `phase1/probe-quota/bundle` / 0.1.3-phase1，manifest 要求 `script-tools-v1`，仅声明 `ripple.context.read`，参数空对象。实际重新读取沙盒 schedule.txt，返回事件、revision、SYNTHETIC 来源与动态 retrieved_at。工具没有日程写入分支；诊断审计追加是磁盘副作用，操作员 Seed/Empty 是实验布置，不暴露给模型。不能仅凭 read-only profile 宣称无副作用。

同 id ripple 安装在专用 quota-home/quota-apps，复用原已保存 Provider 的 kernel-core；原正式 bundle、安装状态和历史探针不动。无 Provider 测试用独立空 core，不读取或复制凭据。不同 id phase1.bootstrap 仅用于原生基线启动和平台初始化观察，不作为 Ripple Agent 成功。

0.1.1/0.1.2 保存错误及真实模型记录均保留。0.1.2 采用有界回答与 history 计数；0.1.3 仅增加声明的实验存储至 1 MiB，解决递归 Kernel 工作文件超出 64 KiB 的真实故障。工具及 Agent 指令未改，当前已安装 manifest 哈希为 `0e5d3d37beaa0883fc7cfd8bd54fc9f7278ad4f45447dfd62f2a222ffc7f608b`。

后续首选仍是已验证的官方 app Agent/Splash 工具路径。待完整前置门槛解除后，slots.search 应复用确定性引擎，最多返回三个当前候选；模型只能选择结果中的候选 ID。应用必须校验任务代次、上下文 revision、天气地点/区间/时区/有效期、最新用户限制、未来时间与时长。重新规划使旧提案失效，迟到结果丢弃。以上是下一阶段要求，尚未实现。

原版 weather/analyze/proposal/confirm/execute/finish_verify/STALE/FAILED/COMPLETED 保持原样；没有新建审批状态机。Agent 使用许可和单次修改批准必须继续独立。当前没有 slots.search、候选协议、写工具、AI 后端、个人日历或 Google Calendar 写入。

普通干净 App Hub 安装仍阻断，需官方支持路径。完整证据见 PHASE2_AGENT_EVIDENCE.json 与 ../phase1/current/PHASE1_REAL_AGENT_VALIDATION.md。
