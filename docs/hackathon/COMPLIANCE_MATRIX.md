# Competition architecture compliance matrix

Reviewed 2026-09-30. PASS means the stated scope has evidence; it does not imply production integration or complete submission readiness.

Official sources: [competition](https://create.gosim.org/agenticapp26/?lang=en), [pinned host Web card implementation](https://github.com/OctoSense-org/robrix2/blob/05daf9bdb05fafc6d8f04dcb312a35f1d46a661e/src/mini_app.rs), [host authority ADR](https://github.com/OctoSense-org/robrix2/blob/05daf9bdb05fafc6d8f04dcb312a35f1d46a661e/docs/adr/0002-octoscript-mini-app-authority.md), [Octos architecture](https://github.com/octos-org/octos). The event allows Web URL cards, asks for a working Agentic app and public Apache-2.0 source, and names OctoSense-org/robrix2. Its released competition version is not inferred from a development branch.

Rows below apply the user's requested hardening baseline; names of internal states and errors are application contracts, not claims of official mandatory enum names.

| Requirement | Current evidence | Status | Required fix | Verification method |
| --- | --- | --- | --- | --- |
| robrix2 primary host baseline | host-baseline.json, pinned separate official mini-app checkout | PARTIAL | Confirm organizer release and run authenticated card flow | Prepare host; build; + → Share mini app; recipient open |
| Runnable Agentic Web mini app | Clean install, build, 52 tests, browser local demo with real local write/read-back | PASS | None for local Demo scope | COMMANDS_RUN.md and evidence screenshots |
| Chat / Discover / mini-app entry retained | Unmodified pinned host home_screen.rs, mini_app.rs, article_app | PARTIAL | Runtime navigation/Matrix session verification | Host launch on supported target; UI paths |
| Read authorized external state | CalendarCapability.readState; source labels; adapter reads | PASS | Real account validation remains separate | Workflow and adapter tests, Demo browser |
| Propose/prepare bounded action | prepareAction creates frozen source-bound proposal from deterministic engine | PASS | None for current single-event scenario | engine.test.ts, workflow.test.ts |
| Consent before writes | READ via readState; Demo WRITE_REVERSIBLE; real WRITE_SENSITIVE; grant bound to action and capability | PASS | None for in-process contract | Missing/forged/cross-context grants and explicit consent tests |
| Execute through capability | App → CalendarWorkflow → CalendarCapability → adapter | PASS | None | Code inspection plus workflow tests |
| Verify before COMPLETED | readState before execute, readState after, verifyResult before/after/expected; timestamps + preserved identity/metadata | PASS | Real service evidence remains TODO | Write acknowledgement mismatch and read failure tests |
| Expose accurate result | Typed error/retry flag, verification evidence, history-derived UI; no success for failure | PASS | None for tested Demo cases | Browser happy/rejected/failed/stale/mismatch and tests |
| Unified lifecycle | DETECTED → UNDERSTOOD → PROPOSED → AWAITING_APPROVAL → EXECUTING → VERIFYING → COMPLETED | PASS | None | workflow snapshots/history and transition tests |
| Rejection/cancellation | DECLINED and CANCELLED terminal guards, zero writes | PASS | None | Automated tests and browser rejection |
| Failure/partial recovery | FAILED vs PARTIAL; uncertain/acknowledged writes only reconciled by reads | PASS | No automatic rewriting; new mutation needs new proposal | Partial/recheck and execution-failed tests |
| Stale data/time | Canonical facts version, target GET, 10-minute approval validity, future slot, ETag PATCH/412 | PASS | Atomicity across services remains limited | Weather change, time expiry, latest target, conditional update tests |
| Unified error model | Seven codes in errors.ts with retryable flag and uncertain outcome flag | PASS | None for current workflow | Error-specific tests and UI labels |
| No invented weather facts | Missing observations excluded; full dry coverage needed by engine | PASS | None | Missing/null weather adapter tests |
| At least five core workflow tests | happy-path, approval-rejected, execution-failed, state-stale, verification-failed | PASS | None | npm test; npm run test:integration |
| Web route lawful; no arbitrary native import | Existing official WebMiniApp payload; no native package generated | PASS | None for route choice | mini_app.rs + MINI-APPS.md |
| Native capability extensions only if needed | Calendar APIs work in Web route; no Rust added | NOT_APPLICABLE | None | Source/package diff |
| No full ecosystem integration requirement | No new OctoSense dependency/runtime/protocol | PASS | None | package-lock and source inventory |
| Octos integration truthfulness | Deterministic application workflow; no Octos kernel connection | PARTIAL | If an actual Octos agent is required by organizer/judges, use advertised host capability; do not claim it now | Read Octos OUP/runtime docs; organizer clarification; integration test |
| Final product repository reproducible | No Ripple Git repository, remote, branch or commit | FAIL | Initialize/publish entrant repository and freeze a real commit in a later authorized step | Git SHA, fresh clone and CI |
| Host commit reproducible | SHA checked after prepare-host.ps1; Cargo.lock included upstream | PARTIAL | Provision MSVC linker (locked online build failed); stable toolchain not immutable | Host build on provisioned machine |
| Product Apache-2.0; upstream notices retained | Root LICENSE untouched, new source SPDX; original/pinned host MIT unchanged | PASS | Retain license boundaries | LICENSE_AUDIT.md + backup comparison |
| Third-party distribution obligations | 90 lockfile entries inventoried; runtime notices copied in public output | PARTIAL | Full host transitive licenses/assets and ownership check before submission | DEPENDENCY_LICENSES.json; license texts; host dependency audit |
| Source/demo/screenshots/submission artifacts | Local source and five Demo screenshots; no public repo or video | PARTIAL | Public source, frozen release, demo video and host evidence | SUBMISSION_CHECKLIST.md |

The browser/approval boundary is an in-process application control. It is not a server-side security boundary against someone controlling browser JavaScript. Google OAuth remains separate and least privilege is limited by the existing calendar.events scope. No platform credentials are copied into the Web app.
