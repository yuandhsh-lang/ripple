# Ripple 0.6.4 独立复现

本指南对应已发布的 `v0.6.4`，Commit `7e150404a3073a77688d5e1670de018083fe82a4`。认证包已下载、验证并在本机多个独立空 RC6 环境安装。2026-10-14 的新版演示再次使用该包，未修改 Bundle；这不是第二台设备测试。

- [正式发布包](https://github.com/yuandhsh-lang/ripple/releases/download/v0.6.4/app.bundle.pack.json)
- [来源证明工作流](https://github.com/yuandhsh-lang/ripple/actions/runs/38481044405)
- Pack SHA-256：`60a4f96b18f0a95bf024da24aba83b1e57b10f8677128cd841969261386f90d4`
- Bundle BLAKE3：`254c3298e4d4a470223a138f7c334b5eb580f2ae4b80add7b5b0a7058780e777`

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
Invoke-WebRequest https://github.com/yuandhsh-lang/ripple/releases/download/v0.6.4/app.bundle.pack.json -OutFile app.bundle.pack.json
(Get-FileHash .\app.bundle.pack.json -Algorithm SHA256).Hash
hub publisher-unpack .\app.bundle.pack.json --out .\verified-bundle
hub publisher-verify .\verified-bundle
```

哈希必须与本页一致；每个命令的退出码必须为 0。继续按照官方文档的“在本地演练商店流程”建立一次性 catalog：

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

使用次日日期，输入骑行 15:00–16:00、允许窗口 09:00–11:00；固定会议 10:00–11:00 和 13:00–14:00；交流 14:00–15:00、允许窗口 12:00–15:00。全部同日北京，只有骑行户外。视频的天气变化来自明确标记的测试快照，不保证当天 LIVE 天气出现相同降雨。

[演示证据](evidence/presentation-task.json) 保留 LIVE 原始快照、受控变化、工具搜索、协商及实际结果。没有测试重放时，真实天气无风险应保持安静。只有在隔离测试环境才能重放天气；这不是普通用户功能或后台气象事件。

无解后，用户补充骑行允许窗口 14:00–15:00。确认条件时原时间仍是 15:00；新方案需单独批准。预期交流改到 12:00、骑行改到 14:00，固定会议不变；检查 `execution.json` 为 `COMPLETED` 且 `cursor=2`，重新读取的 `schedule.txt` 与 `expected` 完全相同。
