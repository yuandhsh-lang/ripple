# Ripple qualifying submission

Status: **BLOCKED — target GitHub URL not confirmed; not formally submitted.** Replace the repository field only with the entrant's actual confirmed repository after publication. Do not paste a local-only draft as a completed submission.

Project: Ripple

Primary scenario: Calendar

Short description:

Ripple is a deterministic agentic calendar workflow that combines existing events with weather context to detect risky outdoor plans and propose a feasible earlier time. It waits for explicit approval, reads state again before making a change, and verifies the resulting Calendar state through an independent read-back. Its runnable demo exposes stale proposals, denied permission, failed writes and uncertain outcomes without presenting them as success.

Repository: **BLOCKED — entrant GitHub repository URL required**

Commit: **PENDING local freeze; resolve the qualifying tag after commit**

Tag: qualifying-2026-10-04

Host: OctoSense-org/robrix2

Host branch: dev/wechat-octoscript-miniapps

Host commit: 05daf9bdb05fafc6d8f04dcb312a35f1d46a661e

Architecture: React/Vite HTTP(S) web mini app opened through robrix2 web mini-app cards. Native host source is unmodified; Ripple is not an OctoScript native application.

Agentic loop: read → analyze → propose → approve → execute → verify (including a preflight re-read and post-write read-back).

Human control: explicit approval of a concrete proposal; decline/cancel preserves the original plan; changed state invalidates approval; uncertain results use read-only reconciliation.

Real integrations:

- Open-Meteo: **verified real network read** on 2026-10-04.
- Google Calendar: adapter implemented and mock-tested; **OAuth end to end and real write/read-back NOT VERIFIED**. No configured credential is included.

Tests (rerun 2026-10-04): npm ci retry exit 0; npm test 63/63, integration subset 45/45; lint/typecheck/build exit 0. First npm ci failed from a loaded native binding; retry passed after stopping own Vite processes. Remote clean clone: NOT VERIFIED pending publication. See [VALIDATION.md](VALIDATION.md).

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

Formal submission: NOT VERIFIED. Deadline in [current competition rules](https://create.gosim.org/agenticapp26/?lang=en): 2026-10-04 23:59 Beijing time. The linked participation questionnaire is registration, not verified as a qualifying-upload endpoint. Use the organizer's actual submission channel; retain its receipt.
