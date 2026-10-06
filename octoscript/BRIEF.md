# Ripple OctoScript migration brief

App: ripple 0.1.0, Ripple. Existing React files and Git history remain as references.
Target: an ordinary OctoSense store script app; no calendar host service, Google account, OAuth token, React wrapper or Rinx URL card.

## Screens and actions
- A native overview displays the current local test schedule, real weather source/time, workflow status, and verification outcome.
- Load weather from Open-Meteo using explicit latitude/longitude inputs. Validate coordinates; surface HTTP/network/response failures without changing a schedule.
- Create one clearly labelled outdoor test schedule using an actual upcoming rainy forecast hour with an available dry alternative. If no such hour exists, explain why; never fabricate weather.
- Inspect the stored schedule and its duration. Edit its time by a deliberate manual test edit; delete the test schedule to exercise empty.
- Analyze the stored schedule against fresh complete hourly weather. Show the conflict and a same-day earlier dry slot, preserving event identity, location, title and duration. Proposal is pending for at most ten minutes; analysis never writes schedules.
- Confirm is a separate explicit user action. Re-read schedule storage and compare the exact source bytes and weather identity/freshness before any write. Reject stale proposals and invalid inputs.
- Execution writes only the proposed time changes to the app's own schedule storage, then reads the file again and checks the full expected record. COMPLETED appears only after that independent read matches.
- Decline and cancel each end the pending proposal without a schedule write. Keep EMPTY, FAILED, STALE, DECLINED, CANCELLED, AWAITING_APPROVAL, EXECUTING, VERIFYING and COMPLETED visible and distinct.
- Retry weather loading after a failure; repeated confirmation cannot duplicate a write.
- Restart reloads stored schedules and the last verified outcome; old pending proposals do not survive restart as executable approvals.

## Data, permissions, and limits
- storage: only the app's contained test schedule, outcome and audit log. No personal calendar, account token, passwords or external storage. All persisted records are bounded and validated.
- net: GET to api.open-meteo.com only, for hourly weather_code, precipitation and precipitation_probability; seven forecast days, explicit timestamps. Missing/null coverage is never considered dry. Precipitation/probability describe the preceding hour and are aligned accordingly.
- Declared network host: api.open-meteo.com. No location capability; coordinates are user supplied.
- Test schedules are synthetic app-owned data, weather is live Open-Meteo data. State this in the interface.
- Alternative search: same local calendar day, 2.5 to 8 hours earlier, future, duration unchanged, complete dry forecast. No suggestion if any check is unresolved.

## Native acceptance
Use the pinned official Windows card-host, hidden with an isolated storage directory and bridge port 8141. Capture startup, real-weather pending proposal, manual approval plus verified completion, decline, cancel, stale, empty and error. Compare actual jail files before/after no-write branches. Quit and restart to verify persistence. Preserve failed runs and screenshots. Capture final screenshots only through tools/octo shot and inspect their pixels. Run tools/octo check and hub scan; answer all seven review questions outside bundle. Publisher identity/support/privacy and publication remain human checkpoints. Installation currently requires a later Windows restart; final status cannot be PASS until that verification is complete.
