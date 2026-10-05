# Qualifying source-delivery compliance

Reviewed: 2026-10-04 (Beijing time); publication preparation updated 2026-10-05. Overall source delivery: **BLOCKED** pending verified public push. The entrant confirmed [yuandhsh-lang/ripple](https://github.com/yuandhsh-lang/ripple) as the target. Local PASS rows are scoped evidence, never organizer acceptance. This document supersedes the older dated delivery matrix/checklist.

## Official requirements and scope

[Competition rules](https://create.gosim.org/agenticapp26/?lang=en) require public Apache-2.0 code, a runnable prototype, scenario, screenshots/demo and registered team details. Qualifying closes **2026-10-04 23:59 UTC+8**, and judges use the October 4 frozen version. Web URL cards are permitted; supported desktop demos are allowed. Registration is individual, including the captain and each member.

The reviewed rules do not explicitly mandate an LLM, Octos runtime or OctoScript for the Web route. This is a reading of the published text, not an eligibility ruling. Calendar is the primary scenario; weather is context, not a claim to implement the full Weather scenario.

[App Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) and its [publishing guide](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md) describe native App Hub packaging/admission. No current contest rule was found requiring Web entries to produce `main.splash`, publisher keys, signed bundles or an App Hub submission issue. Those publishing operations were not performed.

### Additional organizer-repository audit

Reviewed organizer repository HEAD **`0db87b582438f0f01534435b8537e8c89bcd303d`** on 2026-10-04: README, Rinx/SSO guides, submission/schedule guides and participant-facing source components. This audits entry requirements, not the website's security.

**Correction:** [current Rinx baseline guide](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/rinx-miniapps.md) names **hagency-org/Rinx** and cites the same complete host SHA as Ripple. GitHub's Rinx commit API confirms `05daf9bdb05fafc6d8f04dcb312a35f1d46a661e` exists there. Repository IDs differ (robrix2: 1379088495; Rinx: 1380738107): shared commit provenance does not mean identical repositories or prove the old branch exists in Rinx. Existing host checkout remains untouched; current Rinx runtime and URL-card journey are unverified.

[Submission guide](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/app-hub-submission.md) permits Web source/page/URL-card delivery and does not require prior Hub listing. Icon, author/support and privacy/permission details are required materials. Ripple has an icon and source/permission/failure descriptions; registered author/team, support channel and actual host URL-card evidence remain incomplete. Real-input/action evaluation is not fully established by a demo Calendar plus mocked Google tests.

[Rinx guide](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/rinx-guide.md) describes Matrix/SSO account setup; it adds no Rust, OctoScript or model-API mandate. The reviewed runtime criteria support describing deterministic task automation as agentic, subject to organizer judgment. No registration, login or messages were performed.

**Confirmed collection channel:** [issue #13](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13), requesting team name and entrant repository URL in a comment. This is not Ripple's source repository. No comment was posted; public repository and team identity are not finalized.

## PASS

| Item | Scoped evidence |
| --- | --- |
| Runnable prototype / demo | Credential-free local Demo; production build and prior local browser replay |
| Apache-2.0 | Root LICENSE matches official text after line-ending normalization; README/package license agree; LICENSE unchanged |
| Calendar scenario / weather context | Existing timed event + visible weather facts + pending versus verified outcome |
| Agent loop | Read/analyze/propose/approve/preflight read/execute/read-back/verify, confirmed in workflow and capability source/tests |
| Human confirmation | Source-bound one-use approval; explicit consent for real writes; decline/cancel does not write |
| Failure handling | Stale, permission denial, write failure, mismatch, uncertain outcome and read-only reconciliation |
| Screenshots | Seven required PNGs exist; all thirteen retained PNG/JPG screenshots inspected as demo UI, with no observed credentials/account/calendar private data |
| Open-Meteo | Actual network forecast read on 2026-10-04; normalized 168 points to 167 intervals |
| Local source reproducibility | This run: npm ci, 63 tests, 45 integration-subset tests, lint, typecheck, build; see VALIDATION.md |
| Source audit | Source/config/docs/patches reviewed; dummy test tokens distinguished from runtime variables; no secret identified for staging; generated/cache/credential paths ignored |
| Independent Git | Initialized Ripple as its own main repository; upstream checkouts excluded |
| Exact host baseline | Local clean checkout and remote branch both match the immutable pin below |
| Frozen tracked-file completeness | Local clone of tag/source SHA outside Ripple passed installation and all checks; this does not verify GitHub cloning |

### Host observation

Repository: [OctoSense-org/robrix2](https://github.com/OctoSense-org/robrix2/tree/dev/wechat-octoscript-miniapps).

Branch: `dev/wechat-octoscript-miniapps`.

Local HEAD / remote branch tip: `05daf9bdb05fafc6d8f04dcb312a35f1d46a661e`.

Commands: `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v` in the host; `git ls-remote https://github.com/OctoSense-org/robrix2.git refs/heads/dev/wechat-octoscript-miniapps`.

Actual checkout: **Ripple/.host/robrix2**. The requested sibling `.host/robrix2` does not exist. This matches the project's prepare-host script. No host source, checkout state or branch was changed. A development pin alone does not establish the organizer's released package identity.

## PARTIAL

| Item | Remaining boundary |
| --- | --- |
| robrix2 Web integration | URL-card path and native prerequisites documented; authenticated runtime journey unverified |
| Real integrations | Real weather verified; Google adapter has mocked coverage only |
| Demo delivery | Local runnable rehearsal and screenshots supplied; hosted URL/video not produced |
| License provenance | Standard source license and runtime notices retained; older third-party audit remains partial, and entrant ownership not independently attested |
| Submission material | SUBMISSION.md prepared; repository identity/publication fields cannot be finalized without the target URL |
| Current Rinx requirement | Immutable source commit present in Rinx; runtime, URL-card demonstration and classroom release unverified |
| Required application metadata | Icon exists; registered author/team and usable support channel still need completion |

## NOT VERIFIED

- Google Calendar OAuth end to end and real write/read-back.
- robrix2 sender → recipient real-account journey and native host runtime.
- Android/iOS physical devices; mobile screenshot means browser viewport only.
- Organizer release package identity, team registration/roster, and formal qualifying submission/receipt.
- Clean clone **from the pushed GitHub repository**: impossible before a confirmed remote/push. Local clean-clone validation is separately identified if performed.
- GitHub Actions execution (workflow exists; no remote run observed).

## BLOCKED

- Status update, 2026-10-05 Beijing time: the published October 4 23:59 qualifying deadline has passed. Ripple was frozen locally on October 4, but no public push or issue #13 submission receipt exists. Whether a late repository/comment is accepted requires organizer confirmation; no extension or timely submission is claimed.

- Public source and push: target confirmed as `yuandhsh-lang/ripple` on 2026-10-05. Local checks passed; browser is waiting for the entrant's GitHub login. Repository creation, push and remote verification remain pending.
- Repository visibility, remote README/LICENSE and remote commit/tag cannot be verified before that push.
- Overall contest source-delivery PASS therefore remains blocked. Local tests are not competition approval, and a local tag is not formal submission.

## Freeze and rollback

Freeze tag: **`qualifying-2026-10-04`**, created locally on 2026-10-04, points to source commit **`19ac9b54ee46e5e6bda34ebcfc654637d3edcb87`**. Resolve it with `git rev-parse qualifying-2026-10-04^{commit}`. SUBMISSION.md records this hash in a separate documentation-only receipt without moving the tag: a file cannot contain its own enclosing Git commit hash. This tag does not establish GitHub publication or submission.

Restore the source using a separate checkout of the tag, or inspect/revert later delivery documentation commits. Keep earlier reports/screenshots. Sanitized historical machine paths have originals in a sibling `.hardening-backup` directory outside the repository; no credentials, upstream code or production data changed.
