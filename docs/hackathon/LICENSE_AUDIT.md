# License audit

Audit date: 2026-09-30. Overall third-party audit: PARTIAL. No existing LICENSE or upstream copyright notice changed.

| Scope | Evidence | Finding |
| --- | --- | --- |
| Workspace root | no LICENSE, no Git | Do not apply a blanket new license to the three independent directories |
| Ripple original work | Apache-2.0 root LICENSE and package declaration | Existing Apache declaration retained; source ownership and submission rights still entrant responsibility |
| New capability/workflow/tests | SPDX-License-Identifier: Apache-2.0 | New files follow Ripple's existing license; no invented copyright holder |
| Original robrix2 | LICENSE-MIT, copyright 2023-2024 Project Robius Developers; Cargo license MIT | Retained exactly; not relabeled Apache |
| Pinned official mini-app host | LICENSE-MIT, copyright 2023-2026 Project Robius Developers; Cargo license MIT | Retained exactly in separate checkout; event's broad platform-license statement does not override actual files |
| OctoSense reference | Apache-2.0 root LICENSE, independent subcomponents/vendor licenses | Untouched; not bundled into Ripple |
| Product runtime dependencies | react, react-dom, scheduler actual package LICENSE text | MIT notices/disclaimer preserved in public/third-party-notices.txt and copied by Vite into dist |
| Lockfile inventory | DEPENDENCY_LICENSES.json, 90 entries | MIT 73, Apache-2.0 3, MPL-2.0 12, ISC 1, BSD-3-Clause 1; no missing license metadata |

The 12 MPL entries are lightningcss and its optional platform bindings, existing build tooling. They are not copied as source into Ripple. Do not redistribute modified MPL tool source under Apache alone; retain its obligations if packaging tooling. The [ASF license guidance](https://www.apache.org/legal/resolved.html) lists MIT/ISC/BSD as permissive and MPL under conditional inclusion. This is supporting guidance, not a legal clearance for every possible distribution.

Runtime notices were copied verbatim from installed packages. Lock metadata is evidence of declarations, not proof that every file of every optional package has been inspected. Dev/platform package binaries and full Rust host dependency/assets licenses remain unverified. The host's LICENSE-MIT and licenses directory must travel with any host redistribution; never delete those to satisfy the entrant Apache requirement.

Product source has no added vendored upstream code, image-generation assets, fonts or native packages. Original favicon and UI ownership were not independently established. No dependency added or upgraded by this hardening pass. `package-lock.json` changes only the root Node engine declaration.

Submission action: publish entrant work under the existing Apache-2.0 license, preserve all applicable third-party notices, inspect provenance of original assets, and audit the chosen host distribution separately. No identified root-license conflict was silently repaired; no licenses were replaced.
