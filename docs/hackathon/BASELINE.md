# Reproducible baseline

Audit date: 2026-09-30 (Asia/Shanghai).

| Item | Observed value |
| --- | --- |
| Product upstream repository / remote / branch | UNKNOWN — Ripple has no Git repository |
| Product baseline commit / current commit | UNKNOWN — no Git HEAD exists; no placeholder or invented SHA |
| Original host upstream / remote | https://github.com/Project-Robius-China/robrix2.git |
| Original host branch / baseline / current commit | main / da375f241df3368a24318c94a5ed4865009f7529 / same |
| Primary competition development host | https://github.com/OctoSense-org/robrix2.git |
| Host source branch | dev/wechat-octoscript-miniapps |
| Prepared host baseline / current commit | 05daf9bdb05fafc6d8f04dcb312a35f1d46a661e / same |
| Prepared host checkout branch | dev/wechat-octoscript-miniapps at audit; script detaches when recovering exact pin |
| Official competition released package/commit | UNKNOWN — development branch is not proof of organizer pin |
| Reference ecosystem | https://github.com/OctoSense-org/OctoSense.git, main, 7b03d2f3079777bf48f7dea9e5dd20d5b1f77732 |
| Reference Octos dependency | https://github.com/octos-org/octos.git at 0e6db72d8c8d5f8101535690975b30a3f2cf7249 in OctoSense/Cargo.toml; not linked by Ripple |
| Product runtime required | Node ^20.19.0 or >=22.12.0; npm and browser; OAuth optional for real mode |
| Actual product runtime | Node v24.14.0; npm 11.9.0; Vite 8.3.1; TypeScript version fixed by package-lock |
| Host Rust toolchain | upstream rust-toolchain.toml says stable; actual synchronized rustc 1.98.1 (48a229cea 2026-09-01), cargo 1.98.1 |

Run from the Ripple source directory:

```powershell
npm ci --ignore-scripts
npm run typecheck
npm run lint
npm test
npm run test:integration
npm run build
npm run dev -- --port 5187 --strictPort
./scripts/prepare-host.ps1
```

Use the printed URL. Port 5187 was chosen only for this audit. A new checkout can use another free port; Google OAuth must authorize the exact origin. The Web route requires no Rust or Octos service for the standalone Demo.

Prepare-host creates `.host/robrix2` without touching sibling checkouts, validates its remote and clean working tree, and verifies the exact manifest SHA. If the branch later moves, it fetches and checks out the immutable commit. A dirty or unexpected checkout is rejected, not overwritten.

Host validation attempted from `.host/robrix2`:

```powershell
cargo build --locked --offline
$env:CARGO_NET_GIT_FETCH_WITH_CLI = 'true'
cargo build --locked
```

Results: offline build FAILED because askar-storage revision 49086e28 was not cached. The first online attempt stalled at the ruma Git fetch and was interrupted. The Git-CLI retry fetched locked Git revisions and crates, then FAILED during compilation: MSVC `link.exe` not found. No compatible Visual C++ toolchain was discovered via PATH or vswhere. Install/provision the upstream Windows build prerequisites and retry the locked build before submission. `cargo run --locked` remains **UNVERIFIED**. No native app execution or authenticated Matrix card share was performed. Format for Ripple: NOT_AVAILABLE; no formatter added. Host source unmodified, so no Rust format churn.

For Windows host entry rehearsal, + → Share mini app creates the upstream Web card with Ripple's reachable URL; recipient uses Open in browser. macOS/iOS embedded WebView is source evidence only, not device validation. Do not replace a custom Matrix event with a guessed protocol; use the host's own composer.

`SOURCE_MANIFEST.json` records hashes of the delivered source/configuration/documents (excluding itself, dependencies, dist and .host). It is a snapshot inventory, not a Git commit. Final public-repository provenance remains incomplete.
