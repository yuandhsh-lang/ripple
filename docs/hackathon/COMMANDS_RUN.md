# Actual commands and results

2026-09-30, Asia/Shanghai. No deployment, production write, Matrix message, push, commit or PR performed.

| Command / check | Location | Actual result |
| --- | --- | --- |
| Get-Location | workspace | <historical local workspace> |
| ProviderSwitch.ps1 -Action restore-handoff at mandated path | workspace | FAILED: file not found; no handoff/provider change |
| git status; remote -v; branch --show-current; rev-parse HEAD; log -5 --oneline | root and Ripple | FAILED: not Git repositories |
| Same Git read commands | sibling robrix2, OctoSense | Successful; clean, remotes/SHAs in REPOSITORY_MAP |
| Get-ChildItem; rg --files; Get-Content; targeted rg | workspace/source | Actual manifests, source, licenses, CI, tests inspected; several initially guessed file paths did not exist, then corrected to real files |
| git ls-remote official robrix2 HEAD/main/mini-app branches; GitHub tree API | official repository | Main da375f24; mini-app branch 05daf9bd; inspected immutable source |
| npm test (before edits) | Ripple | 3 files / 20 tests passed |
| npm run lint; npm run build (before edits) | Ripple | Passed |
| ./scripts/prepare-host.ps1 (initial and repeated) | Ripple | Passed; verified 05daf9bdb05fafc6d8f04dcb312a35f1d46a661e; separate clean checkout |
| rustc --version; cargo --version in prepared host | .host/robrix2 | stable toolchain automatically synchronized/installed by rustup: 1.98.1; no source dependency added |
| cargo build --locked --offline | .host/robrix2 | FAILED before compilation: askar-storage revision absent from offline Git cache |
| cargo build --locked (default Git fetch) | .host/robrix2 | Interrupted after stalled ruma Git fetch; no build success |
| CARGO_NET_GIT_FETCH_WITH_CLI=true; cargo build --locked | .host/robrix2 | FAILED exit 1 after fetching locked Git dependencies/crates: MSVC link.exe not found; transient sqlx network errors recovered |
| Get-Command link.exe/cl.exe/vswhere; vswhere VC tools query | local machine | No compatible MSVC toolchain discovered |
| npx tsc -b / npm run typecheck during edits | Ripple | Early old-state tests and TypeScript narrowing errors fixed; final check passed |
| npm test during edits | Ripple | Old transition assertion, a recursive mock, and snapshot-alias test failure diagnosed and fixed; final suite passed |
| npm ci --ignore-scripts (first attempt) | Ripple | FAILED EPERM: audit Vite process held rolldown native module |
| Stop-Process for identified audit Vite PID; npm ci --ignore-scripts | Ripple | Successful clean install, 47 installed packages; lock includes optional platform packages; no dependencies added/upgraded |
| npm run typecheck | Ripple | Final: exit 0 |
| npm run lint | Ripple | Final: exit 0 |
| npm test | Ripple | Final: 5 files / 52 tests passed |
| npm run test:integration | Ripple | Final: 3 files / 39 tests passed; actual local Demo storage and mocked Google/Open-Meteo HTTP; not live external integrations |
| npm run build | Ripple | Final: exit 0; tsc + Vite production bundle |
| npm run dev -- --port 5187 --strictPort | Ripple | Started, browser exercised; stopped before clean install |
| npm run preview -- --port 5187 --strictPort | Ripple | Production app served and browser exercised |
| Browser via connected CUA | local app | Happy path, rejection, execution failure, verification mismatch, stale, cancellation verified; screenshots saved; no captured console error/warn |
| agent-browser availability | local machine | NOT_AVAILABLE; connected browser used without installing another package |
| Format | Ripple | NOT_AVAILABLE: no formatter script/dependency; no second toolchain added |
| CI remote run | Ripple | UNVERIFIED: added workflow, no public repository or push |
| Full native host tests/lint/runtime | prepared host | UNVERIFIED; online build blocked by missing MSVC linker |
| Real OAuth/Calendar/Weather and Octos runtime | external | UNVERIFIED; none executed |
| Backup/file diff/license/dependency comparison | Ripple | No original source file deleted; LICENSE bytes unchanged; dependency entries/versions unchanged; final upstream trees clean |

The integration subset is part of the full 52 tests, not 39 additional tests. Browser checks are local Demo evidence. No video, cross-device share or Google execution claim is made.
