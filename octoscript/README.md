# Ripple OctoScript runtime notes

The canonical app is the repository-root `bundle/`, version 0.1.0. The local prior-stage `octoscript/bundle/` and its historical acceptance scripts are preserved locally and in `build/rescue/`, excluded from the formal Git delivery. The existing React source and Git history remain historical references.

The app uses one synthetic 60-minute schedule in its own storage and actual Open-Meteo forecasts. Analyze creates a pending same-day dry-time proposal without writing the schedule. Explicit Confirm rechecks the source and weather, writes the time, and independently reads and compares the complete stored record before COMPLETED. Decline and Cancel do not write. Invalid coordinates, missing weather coverage, changed source and empty data have explicit states. A verified stored result survives app restart. There is no Google Calendar access, OAuth, personal calendar, AI provider or executable app-agent service.

Only Windows native card-host UI has been tested. The full OctoSense shell and other app platforms remain unverified. Linux was used for the official structural Hub gate, not for app UI acceptance.

## Exact official source revisions

| Component | Commit |
| --- | --- |
| OctoScript-App-Design-Flow | `a5a87d3c3ff305768ae46bc5f6689abb48115cc4` |
| OctoSense-App-Hub | `9e7f0778429125402dcfefef95ba2b01e8de7b94` |
| OctoScript-Makepad | `2cc5ef37d7d6a3d2992673389ce74488f7bb2d87` |
| makepad | `c155f61d0e1600d2ec474209374444a38a09a470` |
| Octoscript | `5991dfae9344589e732b2605b530f788e8bbcd11` |

Use the official [Quickstart](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/QUICKSTART.md) and `tools/setup-native.py` to prepare the pinned workspace, then build `hub` and `card-host`. The tested Windows build used Rust stable 1.98.1, MSVC and Windows SDK 10.0.26100.0. See the root README for the commands in the prepared local workspace.

`tools/native_driver.py --pid <reported-pid>` drives the actual native Makepad remote bridge, not Splash handlers. It supports click, text, scroll and state capture. It verifies the owned PID before acting. Use only synthetic test data. The fixture depends on the current real forecast: a location without a suitable rain/dry pair correctly produces an explanation. The recorded demonstration used approximate Shanghai coordinates 31.23, 121.47.

## Official gate limitation on Windows

The pinned Windows Hub rejects native backslash paths such as `assets\\icon.svg`. Its digest also depends on native separators. These are preserved upstream behaviors; no official source or gate rule was patched. The unchanged pinned Linux Hub passed the root bundle. In the prepared local workspace, `.host/cross-linux/hub-wsl.exe` transparently maps paths and invokes that actual Hub in the existing WSL distribution, propagating its exit code.

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
$env:OCTO_HUB=(Resolve-Path '.host/cross-linux/hub-wsl.exe').Path
python .host/octo-workspace/OctoScript-App-Design-Flow/tools/octo check bundle
& $env:OCTO_HUB scan (Resolve-Path bundle).Path --packet (Join-Path (Get-Location) 'build/review-final.json')
```

A Windows runtime launch temporarily stamps a different manifest digest. Final official Linux check restores the canonical digest. Source, listing, icon and screenshot bytes remain unchanged. After any stamp, verify the final file hashes before committing or signing.

The delivered bundle is unsigned. Publisher-key creation, signing and App Hub Issue publication remain separate human checkpoints; a local PASSED result and public Git version are not organizer approval. The pinned reference card-host does not verify publisher signatures. Once a future release is signed, preview an unsigned copy outside the delivery and do not mutate the signed canonical bundle.

**WAITING_FOR_RESTART_VERIFICATION:** the Microsoft Build Tools installation returned 3010. Native compilation and app process restart passed; a Windows OS reboot and post-reboot check remain unverified.

## Evidence and rollback

The actual 171-second unedited native demonstration is in `submission/video/Ripple-OctoScript-Demo-v0.1.0.mp4`. The formal eight screenshots were produced by official `tools/octo shot` and visually reviewed. Local detailed startup/check/scan logs and hash bindings stay outside the bundle in ignored `build/`; current rescue archives and branches are retained until the owner confirms cleanup.

Main source SHA-256: `9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`. Final bundle digest: `fdfdd22c731d50d987587aa2f7286ab2b9f21922ec32661c62559c7dbddf3338`.

Rollback a public delivery with a new Git revert commit after owner authorization, preserving history. Never reset or force-push the published main branch. Local rescue archives preserve the pre-reconciliation working tree and all verification artifacts.
