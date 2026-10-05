# Ripple qualifying submission

Status: **BLOCKED — GitHub publication verification pending; not formally submitted.** The entrant confirmed the target repository on 2026-10-05. Do not paste a local-only draft as a completed submission.

Status update, 2026-10-05 Beijing time: the published qualifying deadline has passed. The source tag was created locally on October 4, but there is no public-push or qualifying-comment receipt. Late acceptance is NOT VERIFIED and must be confirmed with organizers.

Project: Ripple

Primary scenario: Calendar

Short description:

Ripple is a deterministic agentic calendar workflow that combines existing events with weather context to detect risky outdoor plans and propose a feasible earlier time. It waits for explicit approval, reads state again before making a change, and verifies the resulting Calendar state through an independent read-back. Its runnable demo exposes stale proposals, denied permission, failed writes and uncertain outcomes without presenting them as success.

Repository: [yuandhsh-lang/ripple](https://github.com/yuandhsh-lang/ripple). Target confirmed by the entrant; push/public visibility verification pending.

Commit (frozen source): **19ac9b54ee46e5e6bda34ebcfc654637d3edcb87**

Tag: qualifying-2026-10-04

Freeze provenance: the tag points to the tested source commit above. A subsequent documentation-only receipt records its hash and clone results without moving the tag. GitHub push and remote visibility remain BLOCKED; this local tag is not formal submission.

Host: OctoSense-org/robrix2

Host branch: dev/wechat-octoscript-miniapps

Host commit: 05daf9bdb05fafc6d8f04dcb312a35f1d46a661e

Current organizer host reference: **hagency-org/Rinx**, citing this same exact commit; commit existence verified. Actual prepared checkout remains robrix2 on the branch above. Current Rinx runtime/URL-card journey: NOT VERIFIED. See COMPLIANCE.md.

Architecture: React/Vite HTTP(S) web mini app opened through robrix2 web mini-app cards. Native host source is unmodified; Ripple is not an OctoScript native application.

Agentic loop: read → analyze → propose → approve → execute → verify (including a preflight re-read and post-write read-back).

Human control: explicit approval of a concrete proposal; decline/cancel preserves the original plan; changed state invalidates approval; uncertain results use read-only reconciliation.

Real integrations:

- Open-Meteo: **verified real network read** on 2026-10-04.
- Google Calendar: adapter implemented and mock-tested; **OAuth end to end and real write/read-back NOT VERIFIED**. No configured credential is included.

Tests (rerun 2026-10-04): npm ci retry exit 0; npm test 63/63, integration subset 45/45; lint/typecheck/build exit 0. First npm ci failed from a loaded native binding; retry passed after stopping own Vite processes. A separate local clone of the frozen tag passed npm ci, 63 tests, 45 integration tests, lint/typecheck/build, all exit 0. **Remote GitHub clean clone: NOT VERIFIED** pending publication. See [VALIDATION.md](VALIDATION.md).

Evidence (all are actual **demo Calendar** screenshots):

- [Completed](evidence/review-20261004-completed.png)
- [No feasible slot](evidence/review-20261004-no-slot.png)
- [Write failed](evidence/review-20261004-write-failed.png)
- [Read-back mismatch](evidence/review-20261004-verify-mismatch.png)
- [Stale](evidence/review-20261004-stale.png)
- [Narrow browser](evidence/review-20261004-mobile.png)
- [Narrow browser completed](evidence/review-20261004-mobile-completed.png)

Demo: follow [docs/DEMO.md](../DEMO.md), using npm ci / npm run dev, without external credentials. The working prototype, screenshots and rehearsal are included; no hosted URL/video is claimed.

Known limitations: one timed event/current local day/one weather city; bounded earlier-slot search; no LLM/Octos integration or background monitoring. Real Google Calendar, authenticated robrix2 recipient flow, host runtime and Android/iOS physical devices remain unverified.

License: Apache-2.0

Team/registered members: **NOT VERIFIED — entrant must use the registered captain and member roster in the organizer's form; no private participant details included in source.**

Source maintainer: [yuandhsh-lang](https://github.com/yuandhsh-lang). Support: [repository issues](https://github.com/yuandhsh-lang/ripple/issues), pending publication. Registered author/team identity remains NOT VERIFIED. Icon: public/favicon.svg. Privacy: demo Calendar persists browser-local sample state; real tokens remain in memory; Google events are fetched after authorization; no credentials or real Calendar dumps are included.

Formal submission: **NOT VERIFIED**. Confirmed collection channel: [organizer issue #13](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13), opened September 30. Comment format:

```text
队伍名：<registered team name>
GitHub 仓库地址：<confirmed public Ripple repository URL>
```

This organizer repository is not Ripple's source repository. No comment was posted. Deadline remains October 4, 2026, 23:59 Beijing time. The questionnaire is registration. Submit only with real publication fields and retain the comment receipt.
