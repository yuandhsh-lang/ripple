# 第二阶段只读准备范围

> 历史实验记录（2026-10-10）。本文状态只适用于当时的版本；目录名 `current` 也保留当时含义。后续开发版本与归档说明见[实验索引](../experiments/README.md)。文中原始 JSON、截图、会话和运行目录仅保留本地，本次未纳入 Git；本文不代表 2026-10-12 重新执行了这些验收。

完整第二阶段状态：BLOCKED。本次最小只读实现经实际 SDK ABI 验证，不能当作完整第二阶段 PASS。

源码：phase2/readonly-prep/bundle/（独立实验分支；未安装为正式 Ripple）。保留 context.read，新增 slots.search；没有写入工具、完整规划 UI、审批对接或新执行状态机。
输入只接收 active task_id、实际 context read_token、整数 UTC min_start/max_end 和最多三候选。只允许 1 小时时长、至多 7 天搜索窗、半小时间隔、单个合成目标活动；没有个人日历 free/busy 保证。未知/过期/缺区间/坐标时区不匹配的天气失败。weather.json 由应用/测试操作员准备，不能由模型传入或写入。
输出 ID 由程序产生，含新 search_id、上下文 revision、天气版本/获取时间/有效期、时间权威和确定性检查。独立选择验证拒绝虚构 ID、旧 search、过去时间、数据或天气内容变化；旧提案尚未接入，此处只证明旧搜索 ID 失效。

真实执行证据：phase1/evidence/convergence-20261010-1343/harness-run-12/readonly-slots-actual-abi.json。分类 HOST_PROTOCOL_INJECTION_WITH_FIXTURE_WEATHER；两个工具调用均走真实 SDK submit/pump/complete，模型使用=false。添加新限制产生不同候选，全天雨返回空、非法参数和天气失败不改 schedule。
单独 LIVE 天气请求见 live-weather-request.json；尚未用真实模型完成 context.read → slots.search → 选择 → 原审批流程，明确 NOT TESTED。

下一步只能继续隔离准备与补齐第一阶段平台验收；完整规划/执行集成及第三阶段尚不安全解锁。后续必须保留原状态机，将模型的合法候选选择转换成新待审批提案；Agent 许可不能替代用户批准。
