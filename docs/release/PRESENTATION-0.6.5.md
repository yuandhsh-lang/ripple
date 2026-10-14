# Ripple v0.6.5 — 版本与实机展示

[观看 112 秒高清实机演示](https://github.com/yuandhsh-lang/ripple/releases/download/v0.6.5/Ripple-0.6.5-Product-Demo-HQ.mp4) · [下载正式应用](https://github.com/yuandhsh-lang/ripple/releases/tag/v0.6.5) · [安装与任务复现](REPRODUCTION.md)

## 固定应用

| 项目 | 对应值 |
|---|---|
| Version / Tag | `0.6.5` / `v0.6.5` |
| 应用 Commit | `f27f0682ee31530967240d4016eba005cec4078f` |
| Pack SHA-256 | `75030807fa1ca6e6f93b52eb44a6ba794956fbdd8145720092f795b440592360` |
| Bundle BLAKE3 | `fe2075c01cf545bc1c191ba0453d6d85b8e8ba3c1b6fbc7b8b1447dbc51bf1cd` |
| GitHub 来源证明 | [官方发布工作流](https://github.com/yuandhsh-lang/ripple/actions/runs/38508531229)，证明对象是发布 Manifest（包含 Bundle 摘要） |
| 视频 SHA-256 | `799a801f9720082efcac062a9e2def380932b7ada4ffde72819b0dbae79e1d42` |
| 视频规格 | 112 秒，1920×1080，30fps，H.264 / AAC，中文解说及烧录字幕，5,581,618 字节 |
| 实机 | 官方 Windows OctoSense RC6；从上述 Release 实际下载、验证并安装 |

## 一次任务的实际结果

通过原生文件选择器导入两场 ICS 会议，再用自然语言创建骑行、阅读和固定项目会议。实际读取 LIVE 天气后，明确标记的 FIXTURE 快照重放原活动时段的降雨风险。Agent 调用上下文和候选搜索工具，说明上午窗口无解，询问新的允许时段。

用户确认骑行可以安排在 12:00–13:00 后，Agent 重新提出两项调整；用户另行批准完整变更。骑行由 09:00 改到 12:00，阅读由 12:00 改到 14:00；内部固定会议与两场外部会议保持不变。执行收据 `COMPLETED / cursor=2`，两项均 `CONFIRMED`，独立读取的计划字节与批准结果一致。查看执行历史后，退出整个宿主并重启，计划、收据、ICS 快照及历史均保持一致，不重复执行。

视频只使用实际 Ripple 与官方 Glance 画面，剪除等待，审批动作的局部慢放有明示。LIVE / FIXTURE 边界在画面与字幕中标注。完整解码、黑帧检测、逐镜头视觉检查及全片实际播放已完成；静止部分是阅读计划和审批结果，不当作模型即时响应。字幕中的模型称谓统一为 Agent，实际 Provider 由证据记录。

[同一次任务的脱敏工具与执行证据](evidence/v0.6.5-task.json) · [真实截图目录](../media/v0.6.5/) · [ICS 示例](https://github.com/yuandhsh-lang/ripple/releases/download/v0.6.5/Ripple-Demo-Calendar.ics)

## 发布与媒体关系

应用 Tag 与签署包先固定，正式包实测和视频随后完成，以新的 Release 媒体附件及 main 文档提交补充。main 的这些文档和截图没有改变 `bundle/`；Tag 中的旧展示是历史内容，以本页为新版媒体索引。

旧 [v0.6.4 展示](PRESENTATION.md) 和所有旧资产保留。GitHub 发布不表示 App Hub 已收录；审核状态以 [#94](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/94) 为准。[支持范围](KNOWN_LIMITATIONS.md) 适用于当前版本。
