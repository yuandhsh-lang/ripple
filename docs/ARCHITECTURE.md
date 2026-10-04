# Ripple architecture

UI → CalendarWorkflow → CalendarCapability → Calendar/Weather adapters → external state.

The app retains the existing deterministic weather/event engine and product interface. The calendar workflow is a single application use case, not a new Agent framework. There is no model API or Octos kernel integration. A future actual Octos host integration must use the host's advertised capabilities and approval policy; no custom protocol is defined here.

`CalendarWorkflow.detect()` reads state, records DETECTED/UNDERSTOOD, prepares an immutable action, then records PROPOSED/AWAITING_APPROVAL. UI subscribes to snapshots and projects real history; it does not invoke Calendar PATCH. No suitable proposal leaves UNDERSTOOD with a no-action message, never COMPLETED.

`CalendarWorkflowCapability` supplies readState, prepareAction, executeAction and verifyResult. READ operates on authorized context. Demo changes are WRITE_REVERSIBLE; Google Calendar changes are WRITE_SENSITIVE. Both require confirmation, and sensitive writes require explicit consent. In-memory grants are bound to prepared action identity, its captured source state and capability instance. A forged, missing, reused or cross-context grant cannot execute. The UI confirmation sheet states exact event and before/expected timestamps. OAuth is separate; approval cannot bypass Google authorization.

Execution consumes one grant, re-reads both sources and the target GET, checks exact canonical source facts, original event times, a future proposed slot and a 10-minute proposal validity. Google sends If-Match from the target ETag; 412 is STATE_STALE. Demo compares the expected original event before storing. Other events are paginated rather than silently omitted after the first Calendar page. Weather gaps never become fabricated dry values.

Only after execute returns does the workflow enter VERIFYING and read state again. verifyResult compares before/after/expected event identity, title, location, timezone, source, all-day flag and start/end. An acknowledgement alone cannot complete. An unchanged mismatch is FAILED; partial mutation or unavailable read-back after a possible write is PARTIAL. COMPLETED requires successful read-back. This verifies the event's time change; it does not provide an atomic transaction spanning Calendar and Weather or guarantee that third parties cannot change them immediately afterward.

States: DETECTED → UNDERSTOOD → PROPOSED → AWAITING_APPROVAL → EXECUTING → VERIFYING → COMPLETED. Exceptional outcomes: DECLINED, FAILED, PARTIAL, STALE, CANCELLED. Transitions are guarded by stateMachine.ts and workflow preconditions. DECLINED/CANCELLED/STALE cannot execute. There is no FAILED → EXECUTING shortcut. Checks of uncertain outcomes are reads only and require a prior uncertain/acknowledged write attempt; definite failures need a new workflow/proposal/approval to write again.

Refresh of a waiting proposal invalidates changed facts, and a failed refresh records a typed failure. UI refresh after a terminal outcome creates a new workflow, clearing old success evidence before new observations. Demo weather fault changes remain stable across reads. Google adapters capture the OAuth authorization generation; reconnecting invalidates the prior adapter before another request. Source context changes create a new workflow; old approvals are not carried across accounts/modes.

Error codes: PERMISSION_DENIED, USER_DECLINED, STATE_STALE, EXECUTION_FAILED, VERIFICATION_FAILED, DEPENDENCY_UNAVAILABLE, INVALID_INPUT. retryable describes whether retry/re-read may help, never authorization to repeat a write. outcomeUnknown flags transport/server uncertainty. UI displays failure, partial, stale or cancellation, and exposes verification and source timestamps. A failed write is not labeled successful.

Google token remains in memory, client ID stays public configuration, and demo state uses a dedicated localStorage key. No Matrix credentials or host session are imported. Browser-side consent is application control, not a defense against someone modifying client JavaScript. Reload loses workflow records; there is no custom memory/database added.

Host and reproducibility evidence is in hackathon/BASELINE.md. Tests use existing Vitest, including actual Demo adapter storage operations and mocked real-service HTTP. Real OAuth/Calendar/Weather and native host execution remain unverified.
