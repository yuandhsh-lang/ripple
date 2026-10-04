# Ripple demo rehearsal

From Ripple: `npm ci`, `npm run dev -- --port 5187 --strictPort`. Open the printed URL. Demo data is explicitly labeled. After the day's alternative time has passed, the existing Demo date logic uses the next day so the proposed slot stays in the future.

1. Reset Demo. Check 15:00 outdoor tennis, forecast rain 14:30–16:30 and suggested dry 12:30.
2. Choose 查看更改. Review the event, original/proposed times, reason and sources.
3. Choose 确认更改. The workflow executes a local Demo write, independently re-reads Calendar and then exposes 已完成 / read-back evidence.
4. Reset; choose 保留原时间. DECLINED leaves the original event and removes approval.
5. Reset; Settings → 日历与数据源行为 → 日历接口失败; close Settings and approve. FAILED / EXECUTION_FAILED leaves 15:00. No success seal.
6. Reset; select 更新成功返回 · 回读结果不一致; approve. FAILED / VERIFICATION_FAILED, independent GET stays at 15:00.
7. Reset; Settings → 立即改变天气. STALE removes approval. Recalculate for a fresh proposal.
8. Reset; open review and 取消. CANCELLED, no write.

检查结果 is a read-only recovery control for an uncertain or acknowledged write. Definite rejected/failed requests do not gain new authorization through it. Another write requires recalculation and review.

Steps above were exercised locally during this audit (except real external services). Screenshots and command evidence are in hackathon/evidence and hackathon/COMMANDS_RUN.md. No video was recorded; the runnable rehearsal and screenshots are supplied.

Host rehearsal (UNVERIFIED): prepare `./scripts/prepare-host.ps1`, provision/build the pinned host, sign into a Matrix account, use + → Share mini app with Ripple's URL, then open the received card. Windows uses Open in browser; macOS/iOS embedded preview needs separate device validation. Use a reachable HTTPS URL for other machines. This audit did not send any messages or deploy a site.

Real-service rehearsal (UNVERIFIED): configure the public Google client ID and exact allowed origin; use a dedicated test calendar/account and explicitly authorize the intended write. Then test consent, a real ETag update and GET verification. Do not use demo screenshots as evidence of Google/Octos execution.
