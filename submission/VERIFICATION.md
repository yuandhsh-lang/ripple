# Ripple 0.1.0 native submission verification

The canonical app is root `bundle/`. This Git delivery preserves the actual visible native OctoScript version shown in the unedited [2:51 demonstration](video/Ripple-OctoScript-Demo-v0.1.0.mp4). Existing React source and dated contest documents remain historical references.

## Immutable file identity

- `bundle/main.splash` SHA-256: `9a6d646eb0a8d175c34854808f1c91717858d584b35b5216a4970a4865b3f011`
- Final Linux Hub bundle digest: `fdfdd22c731d50d987587aa2f7286ab2b9f21922ec32661c62559c7dbddf3338`
- MP4 SHA-256: `38f8e4c0352302e67f62480e2802cd2e7c046861e54999bfd234d4ec281ead60`
- MP4: 171 seconds, H.264, 1080 × 1440, no audio, 2,021,329 bytes. It was actually played, fully decoded without errors, and visually reviewed for the complete workflow and privacy.
- All 12 formal bundle files match the frozen bundle used for acceptance and recording. The eight listing screenshots are direct official runtime captures and were visually inspected.

## Revalidation before Git commit

At 2026-10-06 14:57 UTC+8, root `bundle/` was launched visibly through official `tools/octo run`, port 8141: native PID 40300 reported `admitted` and `ready: first frame drawn`. Actual native click/type/scroll input exercised real Open-Meteo loading, pending proposal without write, Decline, Cancel, changed-source STALE, explicit Confirm, execution, independent storage read-back, invalid-coordinate failure without write, and EMPTY. The app was closed and restarted as PID 7536; COMPLETED / READ-BACK VERIFIED returned and the stored record hash was unchanged.

The revalidation used approximate Shanghai coordinates 31.23, 121.47. The updated live forecast yielded a 10/9 16:00–17:00 test event and 13:30–14:30 alternative, UTC+8. The earlier recorded live forecast yielded a different test date/time; no source changes or mock forecasts were used. The test schedule was removed after revalidation.

The unchanged pinned official Linux Hub was executed through the documented local WSL path launcher. Final official `tools/octo check bundle` returned exit 0, with no `[refused]`:

```text
ripple 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"net", "storage"}, hosts {"api.open-meteo.com"}, storage 65536 bytes, agent none
```

Final `hub scan` returned exit 0 and generated a seven-question packet outside the bundle. No external reviewer or official Hub approval is claimed. Detailed check/startup/scan records, native assertions, raw captures and rescue archives remain in ignored local `build/`.

## Scope and limitations

Windows native card-host is the tested app platform. The full OctoSense shell and other platforms remain unverified. Scheduling uses app-owned synthetic storage, not Google Calendar. No AI-provider or executable app-agent behavior is claimed. See [privacy](../PRIVACY.md) and [runtime notes](../octoscript/README.md).

This release is unsigned. Publisher key creation and signing have not occurred; App Hub Issue publication and competition acceptance have not been confirmed. Publishing a Git commit/tag does not imply Hub approval or an on-time competition submission.

**WAITING_FOR_RESTART_VERIFICATION:** the MSVC/SDK installer returned 3010. App process restart passed; Windows OS reboot and post-reboot verification remain pending.
