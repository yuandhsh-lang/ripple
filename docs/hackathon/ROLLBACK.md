> Historical evidence; machine paths sanitized for publication on 2026-10-04. Originals retained in a private sibling backup. Current delivery status: [COMPLIANCE.md](COMPLIANCE.md).

# Local rollback

Pre-edit source/config/documents archive: `<local pre-edit archive>`. Original inspection backup also exists in `<local private inspection backup>`.

No source file was removed. Original LICENSE is byte-identical. Sibling hosts were not modified, so they require no rollback. The new .host/robrix2 checkout is isolated and can remain as a reference.

To undo this pass: stop the local audit preview server, extract the archive to a separate temporary directory, inspect evidence/hardening.diff and FILES_CHANGED.json, then copy only the listed modified original files back into Ripple. Compare any later user edits first; do not overwrite them blindly. Newly added files may stay unused after restoring the original App/manifest, or be removed individually after review. Never delete the entire Ripple/source directories.

Restoring package.json/lock restores the original scripts/Node metadata; no dependencies were added/upgraded. Reinstall with the lockfile and run the original npm test/lint/build commands. Build output and demo browser-local state are not source backups; reset Demo for the original sample.

The incidental upstream stable Rust toolchain auto-install is a machine toolchain event, not a product source change. No credential, production data, DNS or deployed resource needs rollback.
