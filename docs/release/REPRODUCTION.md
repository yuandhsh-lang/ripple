# Ripple 0.6.5 独立复现

本指南对应 `v0.6.5`。使用该 Tag 的 `app.bundle.pack.json` 与 `release-receipt.json`，核对完整 Commit、Pack SHA-256 和工作流运行地址。正式包已通过下载验证和官方 RC6 隔离安装；[版本与媒体校验](PRESENTATION-0.6.5.md) 提供哈希及实机对应关系。旧版指南保留在 [v0.6.4 固定源码](https://github.com/yuandhsh-lang/ripple/blob/v0.6.4/docs/release/REPRODUCTION.md)。

公开商店收录仍以 [App Hub #94](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/94) 的实际审核结果为准。

## 环境与安装

1. Windows x64，安装官方 [OctoSense desktop-v0.1.0-rc.6](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.6)。这是官方预发布宿主，不是稳定版；本项目不修改它。保留已有安装和数据。
2. 从 [Ripple Releases](https://github.com/yuandhsh-lang/ripple/releases) 下载指定 Tag 的 `app.bundle.pack.json` 和 `release-receipt.json`。对照 SHA-256、Commit 和 GitHub Actions 来源证明。
3. 用当前官方 Hub 运行 `hub publisher-unpack app.bundle.pack.json --out <新目录>`，再对该目录执行 `hub publisher-verify <新目录>`。失败立即停止，不手改摘要/签名。
4. App Hub 正式收录前不能假定它已出现在公共商店。按官方 [本地商店演练](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/main/docs/PUBLISHING.zh-CN.md) 在独立空数据环境安装被验证的发布包；保留其来源证明，不替换成自签应用。本机已完成此路径：只为隔离目录签署 catalog，不重签应用。具体命令见下方。
5. 宿主配置可用 DeepSeek Provider，授权 Ripple Agent；密钥只在宿主安全配置，不写进 Bundle。允许声明的存储、Open-Meteo 网络、只读工具和 Glance 能力。无 Provider 时只能运行手动/规则能力。

## 普通任务

输入“明天下午三点在北京骑车一小时，允许调整到上午九点至十一点，最好上午完成”。等待真实 AI 草稿，核对活动、日期、允许窗口与软偏好；搜索并选择“北京 · 北京市 · 中国”，确认保存。计划列表应立刻显示持久化结果；重启后仍可读取。

需要关联安排时，可在同一次输入中一并描述同日十点至十一点固定会议及其他活动，逐项核对固定/可移动后保存。Ripple 在保存后检查冲突及已保存活动天气。没有风险时保持原计划，不强行生成建议。

出现风险时，检查活动时间、地点、Open-Meteo 来源和获取时间；Glance 若获宿主允许会显示卡片与提醒。点击进入应用。若已打开应用未自动定位，点击“查看系统提醒状态”。

查看 AI 方案或无解说明。没有合法候选时可以明确修改允许窗口/时长；确认新条件后必须重新规划。核对完整变更：活动、原时间、新时间、影响范围。单独点击“批准并执行以上全部调整”。只在逐项独立读回匹配后接受“已核验”。

## 导入已有日历与查看历史

点击“导入已有日历（ICS）”，用系统文件选择器选择 UTF-8 ICS。核对事件数量、来源与时间范围。最多 32 项、32 KiB；UTC / Asia/Shanghai 普通同日事件和单日全天事件。复杂重复规则、未知时区或非法文件会整体拒绝并保留原快照。导入是只读占用，不会改写外部会议。新导入改变相关事实后，旧批准失效。

批准一次实际改期并完成独立读回后，打开“执行历史”，核对授权、原/新时间和核验结果。重启后再次打开查看。最近 32 条摘要不是完整台账；历史不完整时以执行收据和实际计划为准。

## 核验与异常

隔离测试的应用数据位于所指定 APP_DATA 下的 `ripple/`：`schedule.txt` 是权威计划，`execution.json` 是逐项收据，`weather.json` 是天气依据。比较收据最终 expected 与重新读取的 schedule 字节；完成项应有真实读回结果。不要在默认用户数据上注入测试。

拒绝：计划字节不变。重复批准：不能再次写入。提案后修改相关计划或等待天气过期：旧批准失效。中断后：重启只读核对，不能自动执行剩余项。部分失败/未知结果：保持原收据，核对实际成功项，明确处理后才能重新规划。

## 真实网络与重放

LIVE 需要 Open-Meteo 网络；真实 AI 需要 Provider 授权。不能保证演示当天自然产生降雨风险。若使用受控天气快照，必须在界面/视频及记录中标“受控天气重放”，保留 LIVE 原始响应单独证据。故障注入仅用于隔离测试，不称为真实网络故障。

本机独立空环境不等于另一台设备；macOS、Linux、另一台 Windows 设备未验证。

## 验证发布包并建立隔离镜像

以下使用官方 Hub 命令，来自已验证的 [官方发布流程](https://github.com/OctoSense-org/OctoSense-App-Flow/blob/d0344682df7c52ae5a79055f20f148f542d115e0/docs/PUBLISHING.zh-CN.md)。使用 PowerShell 7；先从官方 App Flow 获取相应 Hub 工具。当前验证的 Hub Commit 为 `386359153ed6377b5f047bd9ed2767a6a2ac2bc7`。所有目录均须新建，不指向默认宿主数据。

```powershell
# 在新的工作目录执行，hub.exe 在 PATH 中
Invoke-WebRequest https://github.com/yuandhsh-lang/ripple/releases/download/v0.6.5/app.bundle.pack.json -OutFile app.bundle.pack.json
(Get-FileHash .\app.bundle.pack.json -Algorithm SHA256).Hash
hub publisher-unpack .\app.bundle.pack.json --out .\verified-bundle
hub publisher-verify .\verified-bundle
```

哈希必须与所下载的 release-receipt.json 和 GitHub Release 资产 digest 一致；每个命令的退出码必须为 0。继续按照官方文档的“在本地演练商店流程”建立一次性 catalog：

```powershell
New-Item -ItemType Directory mirror, mirror-keys, runtime
$anchor = (hub keygen .\mirror-keys\anchor).Trim()
hub keygen .\mirror-keys\working
$cert = (hub certify --anchor .\mirror-keys\anchor --working .\mirror-keys\working).Trim()
$origin = (Get-Content .\verified-bundle\manifest.json -Raw | ConvertFrom-Json).integrity.github
hub publish .\verified-bundle --catalog .\mirror\catalog.json --key .\mirror-keys\working --anchor-cert $cert --publisher ("github:"+$origin.repository_id) --repo ("https://github.com/"+$origin.repository) --commit $origin.commit --out .\mirror
hub verify .\mirror\catalog.json --anchor $anchor
```

这组密钥只签署本地商店目录。不要运行 `stamp` 或 `sign-manifest` 改动已封存应用。检查退出码后，在此 PowerShell 子进程设置隔离路径并启动官方 RC6：

```powershell
$rippleRuntime = (Resolve-Path .\runtime).Path
$env:OCTOSENSE_HOME = Join-Path $rippleRuntime 'home'
$env:OCTOSENSE_APP_DATA = Join-Path $rippleRuntime 'apps'
$env:OCTOS_APP_CORE_DIR = Join-Path $rippleRuntime 'kernel-core'
$env:OCTOSENSE_HUB_CATALOG = 'legacy'
$env:OCTOSENSE_HUB = (Resolve-Path .\mirror).Path
$env:OCTOSENSE_HUB_ANCHOR = $anchor
# 从官方 RC6 解压目录运行 octosense.exe
```

在该宿主 App Hub 中安装并打开 Ripple，单独配置模型并授予权限。保留应用所需 `home/apps/kernel-core` 目录，重新启动时使用同样的隔离路径，不复制其他用户的 Provider 数据。退出此 PowerShell 会话即可结束环境变量覆盖。

## 重现视频任务

从 Release 下载 `Ripple-Demo-Calendar.ics`，使用系统选择器导入。示例包含 2026-10-15 13:00–14:00 和 17:00–18:00 两场北京时区外部会议，均为只读快照；第二场以 UTC 编码。选择预报覆盖范围内的同日日期重现时，应同时调整示例 ICS 的日期。

输入三项安排：户外骑行 09:00–10:00，时长 60 分钟，可调整窗口 09:00–11:00、偏好上午；阅读 12:00–13:00，可调整窗口 12:00–15:00；项目会议 10:00–11:00，固定不可移动。核对草稿，搜索并选择北京，明确保存。保持外部会议只读。

演示先实际取得 LIVE Open-Meteo 167 小时预报，上午无降雨。为验证变化响应，在同一个隔离任务中，明确标为 FIXTURE 的天气快照将 09:00–10:00 设为降雨，其他时段沿用取得的事实；不是实际天气突然改变。普通使用没有风险时应保持原安排，不强制产生建议。测试重放不是普通用户功能或后台监测。

AI 通过上下文及候选搜索工具确认原窗口无解，用户在原编辑入口补充骑行 12:00–13:00 的允许窗口，原定时间仍为 09:00。重新规划后：骑行改到 12:00–13:00，阅读改到 14:00–15:00，内部固定会议及 ICS 两场会议不变。核对完整变更后单独批准。

检查执行收据为 `COMPLETED`、`cursor=2`，两项为 `CONFIRMED`，重新读取的 `schedule.txt` 与 `expected` 字节相同。打开执行历史，核对批准和两项独立核验；退出整个宿主后用相同隔离路径重启，计划、外部占用、收据及历史继续保留，不重复执行。

[同一次任务的脱敏证据](evidence/v0.6.5-task.json) 和 [正式媒体对应关系](PRESENTATION-0.6.5.md) 可独立核对。另一台设备尚未实测。
