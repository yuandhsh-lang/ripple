# Ripple 0.2.2-stage1 local privacy notice

This unpublished local build manages one activity entered by the user. It has no external calendar integration or publisher backend.

Ripple stores the activity title, UTC start/end, coordinates, stable identity and revision in its host sandbox. It also stores one forecast, one pending choice, one execution receipt and diagnostic records capped at approximately 24 KB. The manifest storage grant is 1 MiB. The host may additionally persist Agent conversations and tool records; those records are subject to host retention, which Ripple does not delete.

Selecting Analyze fetches live Open-Meteo weather using the entered coordinates. Open-Meteo receives coordinates and connection metadata. After host permission, the selected Provider receives the activity title, times and location, verified weather impact, and search candidates through private App Tools. Ripple does not read or change Provider credentials.

Only Save activity and an explicitly approved change can write the Ripple activity. Independent storage read-back is required to display COMPLETED. Decline and cancelled or expired planning cannot write the activity. Pending approvals are not resumed after restart.

The listing's example.invalid URL is an intentional local-fixture placeholder required by the official listing schema, not a published privacy-policy endpoint. This file covers the current build; the repository's frozen v0.1.0 PRIVACY.md covers only the frozen submission. A public release requires a real current notice and human approval. No public release is performed by this development task.

Local acceptance evidence uses operator-entered demonstration activities and may contain their titles, locations, times and model/tool replies. Do not share these records with personal data. No credentials are included in the bundle or acceptance records.
