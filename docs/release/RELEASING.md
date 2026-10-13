# 发布与回退

只发布根 `bundle/`。拟用正式语义版本 `0.6.4` / `v0.6.4`，尚未创建公开标签或 Release。保留 `v0.1.0` 和所有历史标签。

发布前运行官方 `tools/octo check bundle`、`hub scan bundle --packet <仓库外路径>`，完成 `review/ANSWERS.md`；运行 SDK 严格串行、Web、隔离、lint、类型和构建，并在官方 RC6 空环境实际安装。`card-host` 不支持本应用的真实 Agent，不能代替 RC6 验收。

`.github/workflows/publish-app.yml` 由当前官方 App Flow 模板生成，固定 Hub 提交和 GitHub Actions SHA。只有新 `v*` 标签 push 才触发。prepare job 只读；publish job 只为来源证明及发布资产启用 contents/id-token/attestations 写权限。无需开发者私钥，不能用本地 ZIP 冒充证明包。

必须先取得用户对具体 Commit、新标签和公开操作的授权，才能 push。工作流成功后下载 `app.bundle.pack.json`，核对 SHA-256、BLAKE3、Attestation，再用 publisher-unpack/verify。下载包在全新官方宿主环境重新安装、实际 Agentic 与安全验收通过后才能录制唯一正式 MP4。

正式视频 <120 秒，真实操作、审批不可省略，受控天气明确标记。后续把同一视频 SHA-256 用于官方提交和用户自行上传 B站。更新原 Issue #94 需要单独明确授权，不新建重复提交，不改官方目录或历史评审。

已发布标签不可覆盖。发布包若有 Bug，修复后升版、重做验证和视频。未发布本地修改可用 `git show <已知提交>:<路径>` 对照恢复，先保存当前改动；不要 reset --hard 或删除用户数据。0.6.4 数据 schema 3 没有新增迁移，历史 v0.1.0 不可假定读取新版数据，旧版本只在独立数据环境启动。
