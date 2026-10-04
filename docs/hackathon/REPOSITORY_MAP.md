# REPOSITORY_MAP

Audit date: 2026-09-30 (Asia/Shanghai). Phase 0 inspected code before source edits.

Workspace: `<historical local workspace>`. It is NOT a Git repository. Its initial top-level directories were `Ripple`, `robrix2`, `OctoSense`. No workspace-root README, LICENSE, manifest or CI.

| Directory | Actual role | Remote / branch / HEAD at takeover | Working tree |
| --- | --- | --- | --- |
| Ripple | React/TypeScript Web mini app | UNKNOWN / UNKNOWN / UNKNOWN: no .git | No Git status or history available |
| robrix2 | Original Matrix host checkout | https://github.com/Project-Robius-China/robrix2.git / main / da375f241df3368a24318c94a5ed4865009f7529 | Clean |
| OctoSense | Upstream ecosystem reference; not a Ripple dependency | https://github.com/OctoSense-org/OctoSense.git / main / 7b03d2f3079777bf48f7dea9e5dd20d5b1f77732 | Clean |

Original robrix2 last five: da375f24, cc624888, 021fef8a, 2c523dd7, a2353388.
OctoSense last five: 7b03d2f, 2b716d9, c59193f, f545b26, d1596d7.

## Product code evidence at takeover

- `src/App.tsx`: actual read/propose/approve/PATCH/GET/retry orchestration in React callbacks. UI directly selected adapters and executed writes. Existing verification compared start/end, but state ownership, error classification and approval lived in UI.
- `src/domain/model.ts`, `engine.ts`, `stateMachine.ts`: typed event/weather/proposal/run, deterministic weather overlap and free/dry slot algorithm. Old statuses OBSERVING/ANALYZING/APPROVED/DENIED/EXPIRED. FAILED allowed direct EXECUTING retry.
- `src/integrations/demoCalendar.ts`: localStorage demo event with failure injection, actual local update and GET.
- `googleCalendar.ts`: Google Identity Services token in memory; calendar.events OAuth; list/PATCH/GET primary calendar. No ETag guard or pagination initially.
- `openMeteo.ts`: keyless geocoding + UTC hourly forecast; missing precipitation/probability initially defaulted to zero.
- Runtime: React 19, Vite 8, TypeScript 6. No LLM, Octos client, MCP, custom agent kernel, native app package or Rust product code.
- Tests: existing Vitest, 3 files / 20 passing tests at takeover. No second framework needed.
- Manifest/lock: `package.json`, `package-lock.json`; root Apache-2.0 LICENSE. No initial Ripple CI.
- Documentation: README, `docs/ARCHITECTURE.md`, `docs/DEMO.md`; their claims were checked against code.
- External endpoints: accounts.google.com/gsi/client; www.googleapis.com/calendar/v3; geocoding-api.open-meteo.com; api.open-meteo.com. Demo only writes a dedicated browser-local key.

## Host evidence

Original `robrix2/Cargo.toml`: package robrix 1.0.0-beta.1, MIT; rust-toolchain 1.97.1. `src/home/room_screen/interactions.rs` opens ordinary links via robius_open. No mini-app module/Discover application implementation found at that HEAD. It is not the mini-app development baseline.

Original CI: `.github/workflows/{main,builds,release,distribution-check,deploy-book}.yml`; Rust tests, clippy, spec guards and UX harness exist. Unmodified; not rerun as Ripple tests.

OctoSense has Cargo workspace, Apache root LICENSE and apps/desktop/phone/ROM CI. `Cargo.toml` pins octos-core/cli/research to 0e6db72d8c8d5f8101535690975b30a3f2cf7249. Actual `crates/kernel`, `crates/app-peers`, `crates/shell/src/approvals` own kernel, app access and approval routing. These are reference evidence, not integrations in Ripple.

## Takeover limitation

The mandated ProviderSwitch.ps1 restore-handoff command was attempted before edits. The specified path does not exist on this machine. No handoff was returned; no provider settings or credentials were changed.

## Prepared competition host (after Phase 0)

`.host/robrix2` is a separate, clean checkout from OctoSense-org/robrix2, dev/wechat-octoscript-miniapps, pinned at 05daf9bdb05fafc6d8f04dcb312a35f1d46a661e. `src/mini_app.rs`, `src/article_app`, `src/home/home_screen.rs` and `lab/wechat-ux/MINI-APPS.md` establish Chat/Discover/mini-app entry paths. On Windows, Web cards use Open in browser; macOS/iOS have a native WebView path. No host source edited.
