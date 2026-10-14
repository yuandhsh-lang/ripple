# 0.6.4 当前验收记录

2026-10-14，中国北京时间；本机官方 RC6，新的空数据目录，当前根 Bundle。

| 检查 | 实际结果 | 类型 |
|---|---|---|
| 原始阶段入口严格 SDK |11/11，退出0，无 VM error/预算诊断|固定官方SDK，受控模型/故障|
| 当前根入口严格 SDK |11/11，退出0，无 VM error/预算诊断|相同断言和64ms预算，未修改官方SDK|
| Web |63项通过；集成45项、lint、类型、构建退出0|保留React原型回归，不代替原生|
| 隔离保护 |8项通过|测试环境防护|
| 官方 octo check / hub scan |退出0；unsigned警告；8项人工回答|结构，不是认证或上架|
| 自然语言→城市→保存 |真实DeepSeek工具、Open-Meteo城市选择、读回成功|官方RC6 GUI|
| LIVE天气 |167小时真实响应，测试时原时段0mm/0%|Open-Meteo网络|
| 天气无解协商 |FIXTURE标记9点与15点降雨；真实context/slots，零候选，真实AI询问窗口|真实AI＋天气受控重放|
| 条件确认 |新窗口保存，原时间和关联计划不变|独立读取持久化记录|
| 拒绝建议 |新提案拒绝后schedule与拒绝前相等，Glance撤回|原生GUI＋独立比较|
| 两项独立批准执行 |交流14→12、骑车15→14；固定会议不变，收据COMPLETED/cursor2，实际记录==expected|原生GUI＋独立读取|
| Glance冷应用打开 |真实宿主Toast、卡片；关闭Ripple后点击箭头，GLANCE_OPEN route=risk|宿主原生，未声称Windows通知中心|

历史预算间歇失败未完全归因；当前两次成功不能证明永不超时。暖启动可能需要手动“查看系统提醒状态”。真实非法候选纠错负例未触发，不冒充已验证；SDK对应受控校验通过。部分失败、迟到回调、损坏和重启收据安全由当前SDK全套验证；所有故障并非真实网络事故。

正式 Release 随后已完成来源证明、实际下载和 `publisher-unpack/verify`，并在本机新的隔离原版 RC6 中安装，完成同一任务的真实模型、天气、协商、独立审批、两项写入及读回；参见 [正式交付核验](FINAL_DELIVERY.md)。

2026-10-14 展示修订再次安装同一认证包，所有安装文件逐字节匹配；新任务完成同样闭环，固定会议保持不变。完整宿主中断与重启后，计划及执行收据的 SHA-256 均未改变。新增公开证据见 [presentation-task.json](evidence/presentation-task.json) 与 [presentation-agent.json](evidence/presentation-agent.json)。本轮没有业务修改，不把历史 SDK 故障测试当作本轮重新运行；视频制作检查独立记录于 [媒体清单](PRESENTATION.md)。

审计源：仓库外Final-Delivery-20261014-043017。公开必要脱敏记录置于本目录evidence/；完整私人宿主目录不上传。
