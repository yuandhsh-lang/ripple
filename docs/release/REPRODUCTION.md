# Ripple 0.6.4 独立复现

本文件是操作指南；正式认证包尚未发布，发布后须补充实际 Tag/Commit/包哈希及下载重装记录。源码检查、测试演练包和认证 Release 是不同证据。

## 环境与安装

1. Windows x64，安装官方 [OctoSense desktop-v0.1.0-rc.6](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.6)。这是官方预发布宿主，不是稳定版；本项目不修改它。保留已有安装和数据。
2. 正式发布后，从 [Ripple Releases](https://github.com/yuandhsh-lang/ripple/releases) 下载指定 Tag 的 `app.bundle.pack.json` 和 `release-receipt.json`。对照 SHA-256、Commit 和 GitHub Actions 来源证明。
3. 用当前官方 Hub 运行 `hub publisher-unpack app.bundle.pack.json --out <新目录>`，再对该目录执行 `hub publisher-verify <新目录>`。失败立即停止，不手改摘要/签名。
4. App Hub 正式收录前不能假定它已出现在公共商店。按官方 [本地商店演练](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/PUBLISHING.zh-CN.md) 在独立空数据环境安装被验证的发布包；保留其来源证明，不替换成自签应用。此路径仍需当轮下载包实测后才可标记通过。
5. 宿主配置可用 DeepSeek Provider，授权 Ripple Agent；密钥只在宿主安全配置，不写进 Bundle。允许声明的存储、Open-Meteo 网络、只读工具和 Glance 能力。无 Provider 时只能运行手动/规则能力。

## 普通任务

输入“明天下午三点在北京骑车一小时，允许调整到上午九点至十一点，最好上午完成”。等待真实 AI 草稿，核对活动、日期、允许窗口与软偏好；搜索并选择“北京 · 北京市 · 中国”，确认保存。计划列表应立刻显示持久化结果；重启后仍可读取。

再输入同日十点至十一点固定会议及必要的其他安排。逐项核对固定/可移动，保存。Ripple 在保存后检查冲突及已保存活动天气。没有风险时保持原计划，不强行生成建议。

出现风险时，检查活动时间、地点、Open-Meteo 来源和获取时间；Glance 若获宿主允许会显示卡片与提醒。点击进入应用。若已打开应用未自动定位，点击“查看系统提醒状态”。

查看 AI 方案或无解说明。没有合法候选时可以明确修改允许窗口/时长；确认新条件后必须重新规划。核对完整变更：活动、原时间、新时间、影响范围。单独点击“批准并执行以上全部调整”。只在逐项独立读回匹配后接受“已核验”。

## 核验与异常

隔离测试的应用数据位于所指定 APP_DATA 下的 `ripple/`：`schedule.txt` 是权威计划，`execution.json` 是逐项收据，`weather.json` 是天气依据。比较收据最终 expected 与重新读取的 schedule 字节；完成项应有真实读回结果。不要在默认用户数据上注入测试。

拒绝：计划字节不变。重复批准：不能再次写入。提案后修改相关计划或等待天气过期：旧批准失效。中断后：重启只读核对，不能自动执行剩余项。部分失败/未知结果：保持原收据，核对实际成功项，明确处理后才能重新规划。

## 真实网络与重放

LIVE 需要 Open-Meteo 网络；真实 AI 需要 Provider 授权。不能保证演示当天自然产生降雨风险。若使用受控天气快照，必须在界面/视频及记录中标“受控天气重放”，保留 LIVE 原始响应单独证据。故障注入仅用于隔离测试，不称为真实网络故障。

本机独立空环境不等于另一台设备。未运行的环境或正式包路径必须标记未验证。
