# Ripple OctoScript privacy notice

Version: 0.1.0 · Updated: 2026-10-06 · Publisher: yuandhsh-lang

This notice covers the OctoSense script app delivered in `bundle/`. The older React prototype in this repository is a separate historical reference.

Ripple uses one clearly labelled synthetic outdoor test schedule. It does not connect to Google Calendar, read a personal calendar, request an account login, or collect passwords, OAuth tokens or API keys.

## Data stored on the device

The app's own sandbox stores the test schedule's start/end times, the entered coordinates and a revision value; the last verified expected record; and a bounded audit log of timestamps and workflow states. The storage grant is limited to 65,536 bytes. Forecast data and pending proposals remain in memory. Pending approvals are not resumed after restart.

Analyze, Decline and Cancel do not write the schedule. Confirm checks the current source and weather, writes the approved time, then reads the stored record independently before showing COMPLETED.

Delete test removes the schedule and saved outcome. The bounded audit log remains in the app's storage. Removing all app data through the host's app-data controls, where offered, removes the remaining local files; those host controls have not been verified in the current Windows card-host test environment.

## Weather requests

When you select Load real weather, Ripple sends the latitude and longitude you entered to `https://api.open-meteo.com/v1/forecast`. It requests hourly weather codes, precipitation and precipitation probability. It does not request device location permission. Open-Meteo receives the request and connection information, including the requesting network's IP address. Its handling of those requests is governed by its own [terms and privacy information](https://open-meteo.com/en/terms).

Ripple does not send schedule titles, stored schedule records or its audit log to that service. The app has no publisher-operated backend, analytics, advertising, AI-provider request or other declared network destination.

## Screenshots and support

Acceptance screenshots and a demonstration recording can show the test schedule, entered coordinates, weather and workflow state. Use synthetic data and approximate test coordinates when sharing them. Development logs and runtime test directories are outside the bundle and are not part of the app delivery.

Support: [yuandhsh-lang/ripple Issues](https://github.com/yuandhsh-lang/ripple/issues). GitHub Issues are public; do not include passwords, keys, tokens or personal calendar information in a support report.
