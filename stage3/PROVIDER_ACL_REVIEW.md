# Historical Provider ACL proposal — not executed

2026-10-12 decision: the user explicitly chose not to change historical ACLs this round. Status remains BLOCKED. `evidence/provider-acl-final.json` confirms all five original DACLs are unchanged. No approval is pending.

All paths are relative to `F:\CodexWorkspace\Projects\RipplePhase1-20261010`:

1. `phase1/runtime/kernel-core/profiles/_main.json`
2. `stage2/runtime/kernel-core/profiles/_main.json`
3. `stage2/runtime/runs/audit-20261011-final-01/kernel-core/profiles/_main.json`
4. `stage2/runtime/runs/audit-20261011-final-02/kernel-core/profiles/_main.json`
5. `stage2/runtime/runs/isolation-smoke-20261011/kernel-core/profiles/_main.json`

Evidence: `evidence/provider-acl-before.json` and `evidence/provider-parent-acl.json`. Each inherits Authenticated Users Modify and Users ReadAndExecute. No credential value is included. These are historical configured profiles; all new tests use fresh cores with only an opaque profile copy. No old session/peer/activity is copied or launched.

Proposed smallest first step, only if explicitly approved: protect the DACL of exactly these five files, remove inherited generic-user access, allow only the current owner, SYSTEM and Administrators. Do not change content, ownership, parent directories, host code or configuration values. Back up each exact SDDL first to a new evidence receipt; take before/after SHA-256 without printing file contents. The existing safe ACL receipts are an initial backup, not a substitute for a fresh one at execution time.

Rollback: for each exact path, restore only its saved DACL with FileSecurity.SetSecurityDescriptorSddlForm using AccessControlSections.Access and Set-Acl. Check DACL equality and unchanged content digest. No copies of credential values are required for rollback. Do not recurse.

Acceptance: current owner can open the file; restricted ordinary-group token gets Windows Access Denied; all five content digests unchanged; configured host running as the same user can read a fresh test copy and perform a real model request. A login under an actual second ordinary account is still required for the user's stronger acceptance criterion. No account is available this round.

Limit: parent directories also permit ordinary-user modification. File-only protection reduces direct disclosure but does not prove protection from parent-path replacement, deletion or future host rewrites. Full parent hardening needs a separately reviewed exact directory scope and descendant ACL inventory. Do not call file-only remediation a complete security PASS.

New isolated runs already receive a protected root DACL before the profile is copied. These changes were explicitly authorized. The Windows restricted-token probe opens no credential bytes and does not claim to be an independent account login.
