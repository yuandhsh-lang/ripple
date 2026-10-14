# Ripple 0.6.5 · hub scan 八项回答

对应官方 Hub 386359153ed6377b5f047bd9ed2767a6a2ac2bc7；Bundle 路径 `bundle/`。这是 v0.6.5 的审核回答；发布、下载包复验及媒体状态见对应 Release 证据，不以本文代替审核。结构检查 unsigned PASS 不等于来源证明、实机或正式收录。已发布 v0.6.4 的回答保存在其固定 Tag 中。

1. **描述是否属实？** `main.splash` 的 `interpret_input` / `save_reviewed_draft`（实际草稿入口）、`check_changes`、`app_tool`、`candidate_search`、`prepare_group` / `execute` 和 `finish_verify` / `group_readback` 实现理解、确认、变化规划及执行核验。工具只读。`AGENT.md` 明确不得执行。支持范围与 listing 一致：一个主活动、最多四项关联，最多两项移动，中国同城同日，15–240 分钟。新版另支持用户主动导入最多 32 项、32 KiB 的 ICS 只读占用快照，以及最近 32 条执行历史摘要。不是外部日历同步或不可篡改台账。模型、城市与天气必须网络/授权可用；无全天后台监控。真实证据与受控故障分别列于验证说明。

2. **平台和分类？** productivity 对应计划管理和协调。只声明 windows，在官方原版 RC6 实机验收；不声称其他平台通过。card-host 不提供所需宿主 AI 服务，不能作为完整应用验收。

3. **权限、宿主调用和域名？** storage 保存计划、快照、去重、审批、收据与有界历史，1 MiB；runtime 用于宿主能力发现；octos.session.open / octos.turn.start / octos.turn.interrupt 用于同一个本应用 Agent 与取消；net 仅城市/天气；glance 发布、撤回、列举和消费本应用通知 route。新增 files 权限仅用于用户主动选择 ICS 的 `files.import` v1，不扫描系统文件、不写回原日历文件。`geocoding-api.open-meteo.com` 接收城市关键词，`api.open-meteo.com` 接收坐标和预报参数。Provider 网络由宿主管理，不是应用新增任意域名。无 shell、外部日历账户、GPS 或邮箱权限。用户可不授权 Agent，仍能手动建立/规则分析。随包 PRIVACY.md 与 listing 指向的 v0.6.5 公开隐私页说明 ICS 范围。

4. **是否欺骗界面？** Splash 显示 Ripple；系统通知由真实 Glance 服务生成，应用本身不模仿登录/支付/系统授权页。建议、待批准、正在执行、部分/失败/待核对和已核验分别显示；只有独立读回匹配才完成。天气 FIXTURE 与 LIVE 有标签。listing 清楚披露本地计划和通知限制。

5. **非 agent_files 是否有对助手的指令？** 有：`main.splash` 构造本应用 Provider turn 的解释/规划/一次纠正协议，约束使用当前 task/read/search/candidate ID，禁止写入并要求 JSON。模型和用户输出按不可信数据解析、类型/约束/代际检查。天气仅作为验证数值，不能执行指令。普通界面不会将内部协议展示为必须照做的用户操作；用户源文本不是改变硬约束或授权的依据。

6. **滥用或私人攻击？** 未发现。公开截图只使用操作员创建的演示活动。无模型密钥或真实个人日历。日志公开前检查敏感模式并仅保留本应用测试会话，其他宿主/用户数据不发布。

7. **Agent 范围与工具风险？** 一个 read-only Agent、两个 implemented_by=app/risk=read/private_data=true 的工具 `ripple.context.read` 和 `ripple.slots.search`。返回相关计划、验证天气和合法候选，无发送、删除、消费、外部共享或写日程工具，未设置 shareable。Glance 由应用展示层调用，而非给模型执行权限。已有日程变化经原整组预览和显式批准后由唯一执行路径写入，不能将协商或通知点击当授权。无需 confirm=app 工具，但真实 UI 审批仍保护执行。

8. **建议路由：human-review。** 此扫描回答由开发者完成，不冒充官方 reviewer 接纳。正式包来自标签触发的 GitHub Attestation 工作流，已完成实际下载和官方 RC6 隔离安装。新版媒体与同一次任务证据见 [版本索引](../docs/release/PRESENTATION-0.6.5.md) 和 [新版验收](../docs/release/VALIDATION-0.6.5.md)。Tag 内旧版媒体仅为历史展示，后续媒体提交没有改变签署 Bundle。历史 v0.1.0 初赛评审记录独立保留。
