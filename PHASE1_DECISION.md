# Ripple 第一阶段决策

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](docs/experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

**最终状态：BLOCKED。** 官方宿主、完整实验安装/启动和运行能力查询已有实测；真实 Agent 闭环没有实证，不能判定 PASS。

1. **官方 Windows 宿主是否支持所需 Agent？** RC2 实测存在应用 Agent 会话的许可门禁，完整 Splash 实验可安装运行，`runtime.describe` 确认 app_tools.dispatch@1。官方源码具备 Kernel/应用 peer/模型/工具 relay 路径。仍缺真实模型端到端验证，因此只能确认框架和接口可用，不能声称 Ripple Agent 已运行成功。干净 Store 有能力快照初始化问题，正常打开 Card 基线副本并重开 App Hub 后可以安装，无需修改官方代码。
2. **真实模型是否成功运行？** 未验证。用户报告 Test connection 成功，但当前隔离 Provider 首页没有已保存模型，Kernel profile 为空，没有 Agent 模型会话证据。
3. **模型是否实际调用 Splash 工具？** 没有证据。没有 session_id、真实 tool_call_id、RECEIVED/RETURNED 或模型完成结果。`ripple.context.read` 的业务读取、空结果、异常与迟到处理分支均未被真实模型调用。
4. **下一阶段首选接口？** 官方 manifest 应用 Agent + AGENT.md + tools.json implemented_by=app + requires script-tools-v1 + Splash app_tool(name,call_id)/mod.app_tools.request、active、complete、fail，使用宿主 octos.session.open/history、octos.turn.start/interrupt 的应用 peer 通道。继续固定兼容 Shell/工具链；不以 model.complete 单次响应或 native-direct 队列调用替代 Agent 验证。
5. **需要更换宿主或系统平台？** 对本阶段合成数据只读闭环，暂未发现必须换平台的证据，先解除 Provider/许可阻断。对真实设备日历，RC2 Windows runtime.list 实测 device_calendar 系列 implemented=true 但 supported=false，只支持 macOS/Android；若下阶段选择该官方原生日历接口，需要兼容平台。Google Calendar OAuth 等另一条正式连接路径尚未验证，不能先承诺 Windows 可实现写入。
6. **技术阻断是什么？** 隔离 Provider 未确认保存；Ripple Agent 尚未获允许。其次所有真实模型工具安全场景未完成。Store 初始化顺序已找到正常路径，但它增加可复现性成本。runtime.list 没有 octos 会话 descriptors，发现结果不能代替实际服务调用和授权状态。
7. **第二阶段是否安全开始？** 不能开始完整自然语言计划/执行产品阶段。可继续第一阶段已授权的诊断、准备合成测试和真实闭环；只有 B 成功、必要 C 故障验证完成且 D 仍无损，才解除技术门槛。本实验没有 Google 写入、多 MCP、AI 后端、ROM 或审批状态机改动。
8. **冻结和发布风险？** 存在明确风险。当前已过 10/9 23:59 冻结；本实验 Agent 是冻结版不存在的新功能，不能作为冻结版比赛成绩依据，也不是阻塞性修复自然豁免。公共 App Hub 当前发布路径还要求 GitHub attestation；本地 throwaway 签名 rehearsal 不具有公共准入或 publisher 身份。未改 Issue #94、未发组织方信息、未推送或覆盖发布版本。

## 六关卡的后续限制

按比赛当前文档的六个环节映射；用户未另提供独立六关卡定义。本表是技术约束，不是第二阶段开发。

| 关卡 | 约束与待证明事项 |
|---|---|
| 事件/意图输入与上下文 | 本次只合成沙盒数据；Windows RC2 原生日历不支持。真实数据连接的用户权限、来源、时间与 revision 要独立验证。 |
| Agent 理解与计划 | Provider 必须实际支持工具调用；必须取得模型选择工具和依据实际结果作答记录。声明 tool_calling、通过 Test connection 或编译均不够。 |
| 授权与审批 | 宿主允许应用 Agent 与 Ripple 业务计划审批是两层边界。只读许可不能成为日程修改授权；不得通过环境变量或改 consent 文件绕过。 |
| 执行 | 本阶段没有写工具。RC2 原生日历写方法是 foreground-only，Windows unsupported；Agent 后台回调不能直接获得前台权限。后续应走已有人工审批和正式接口。 |
| 独立结果核验 | 工具 RETURNED 日志只代表提交结果，需与宿主接受/Kernel transcript/模型回答关联。真正执行读回和 STALE 仍需独立、及时的数据读取。 |
| 后续状态/失败/重启 | 官方 script_tools 固定源码限制每应用最多 16 个 pending、最长 60 秒工具 deadline，并丢弃不活跃 call_id 的迟到结果。这些是源码约束，未完成本项目真实故障实测；模型服务超时、重复请求、重启历史和 revision 复用均须验证。 |

当前最少人工事项：在显示中的隔离 `OctoSense [remote]` Provider 窗口保存已测试模型，随后批准 Ripple 的只读 Agent。密钥只输入宿主；不发送到聊天，不复制个人 Provider profile。之后继续 A/B/C，保留真实会话、调用 ID、错误与原版哈希证据。
