# Qualifying validation

Run date: 2026-10-04, Beijing time. These are this delivery's actual reruns, not copied success claims from an old report.

Environment: Windows; Node v24.14.0; npm 11.9.0; locked React 19.3.0, TypeScript 6.0.3, Vite 8.3.1, Vitest 5.0.2, oxlint 1.86.0.

| Command | Exit code | Actual result |
| --- | --- | --- |
| npm ci (first attempt) | 1 | EPERM removing a loaded Windows rolldown native binding; prior Ripple Vite processes were using it |
| npm ci (retry after stopping own preview processes) | 0 | 47 packages installed; npm reported 0 vulnerabilities in its install audit; this is not a complete security clearance |
| npm test | 0 | 5 files, 63 tests passed; start 23:45:58 |
| npm run test:integration | 0 | 3 files, 45 tests passed; start 23:46:01; subset of the 63 tests, includes mocks |
| npm run lint | 0 | oxlint src completed |
| npm run typecheck | 0 | tsc -b completed |
| npm run build | 0 | tsc -b and Vite production build completed; 28 modules; index-Bu6Mr402.js and index-DV_oheqi.css |

No test cases or product logic were changed in this delivery. Extra blank lines at EOF were trimmed from thirteen existing files so the staged whitespace check passes; runtime notice wording was preserved. All five checks were rerun after cleanup and passed again (63 tests at 23:52:01; 45 integration tests at 23:52:07). The installation failure was environmental; retry passed without elevated permissions or dependency changes.

## Earlier browser and real-network evidence retained

The [2026-10-04 functionality review](REVIEW_2026-10-04.zh-CN.md) records actual local browser approval/read-back, decline, denied permission, failed write, mismatch, stale and no-slot flows; a 390 × 844 production-preview completion had no horizontal overflow. It separately records the real Open-Meteo query at **23:01:18 Beijing time**, 168 API points → 167 complete intervals. These browser/network checks were earlier in the same day, not newly repeated by the command run above.

All Calendar screenshots are demo data. Google HTTP tests are mocks, not real OAuth/write evidence. Native host build/run, authenticated card sharing and physical devices remain unverified.

## Reproducibility

Remote clean clone: **NOT VERIFIED** until the entrant repository URL is supplied and push succeeds.

**Local clean-clone completeness: VERIFIED**, 2026-10-04 at approximately 23:53–23:54 Beijing time. `git clone --no-local --branch qualifying-2026-10-04 <local Ripple repository> <new directory outside Ripple>` checked out **19ac9b54ee46e5e6bda34ebcfc654637d3edcb87** into an empty temporary directory. No dependency/cache/configuration files were copied from the development folder.

| Local clean-clone command | Exit code | Result |
| --- | --- | --- |
| npm ci | 0 | 47 packages installed |
| npm test | 0 | 63/63 tests; 5 files; start 23:53:50 |
| npm run test:integration | 0 | 45/45 tests; 3 files; start 23:53:52 |
| npm run lint | 0 | Passed |
| npm run typecheck | 0 | Passed |
| npm run build | 0 | Production resources generated; same JS/CSS asset names as development build |
| git status --short after checks | 0 | Clean; generated files ignored |

This verifies tracked-file completeness and the frozen source's local reproducibility. It does **not** establish GitHub publication or clean cloning from GitHub. Do not quote an unqualified remote clean-clone success.

## Security and evidence

The unchanged LICENSE matched https://www.apache.org/licenses/LICENSE-2.0.txt after CRLF normalization; SHA-256: `3DDF9BE5C28FE27DAD143A5DC76EEA25222AD1DD68934A047064E56ED2FA40C5`.

All publishable files, ignored-path inventory, workflow/adapter implementations and mock-token sources were checked. `.env.example` has only an empty public client-ID setting. No client secret, private key, actual OAuth token, account export or real Calendar dump was identified. Personal local paths in historical report/patch evidence are sanitized in the public copy, with originals retained outside Ripple. Build/dependency caches, credentials/browser profiles and backups are excluded. Final staged content and tracked paths must be rechecked before commit; a pattern scan alone is insufficient.

Screenshot inspection covers all thirteen retained PNG/JPG files; required screenshots and current local documentation links exist. Screenshots show Ripple demo states, without observed sensitive account data. Historical evidence is retained and dated; current documents supersede old missing-Git statements. The initial staged 71-file inventory and full staged patch were checked: no forbidden paths or credential patterns identified; `git diff --cached --check` passed after EOF cleanup. The documentation receipt records freeze/clone results and the later organizer-reference audit in README.md, COMPLIANCE.md, VALIDATION.md and SUBMISSION.md; product source and the tag remain unchanged.
