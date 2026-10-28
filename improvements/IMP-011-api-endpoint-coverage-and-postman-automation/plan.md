# Plan: API endpoint coverage and Postman automation

Date: 2026-10-25
Status: proposed
Level: L
Scope: Implement and release automated endpoint coverage and safe Postman execution across the PF ecosystem.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md)
Related Issue: [#35](https://github.com/mrturo-pf/pf-base/issues/35)
Approved: pending owner decision
Superseded-by: none

## Implementation slices

### 1. Baseline and inventory

- [x] Confirm the current request count, folder boundaries, dependencies, and
  intentional exclusions.
- [x] Export normalized OpenAPI route inventories from `pf-rates` and
  `pf-svc-income` without secrets or live payloads.
- [ ] Define the sanitized `pf-sheets` Web App route inventory, if included.
- [ ] Record all current gaps and stale requests in the Issue and validation
  evidence, not in a second manual register.

### 2. Coverage checker

- [x] Implement a deterministic method/path comparison tool in the owning
  repository (`pf-postman` unless the service contract requires an adapter).
- [x] Normalize path parameters, trailing slashes, and service URL variables.
- [x] Fail on missing, stale, and undocumented duplicate mappings.
- [ ] Add fixtures for valid coverage, intentional exclusion, duplicate request,
  and stale path cases.

### 3. Request assertions

- [x] Add reusable status, response-time, content-type, and JSON parse assertions where appropriate.
- [x] Add JSON and CSV response handling without forcing one response model onto every endpoint; binary and async-job assertions remain pending.
- [ ] Add endpoint-specific required-field and invariant assertions.
- [ ] Preserve chained Preview → Import behavior and assert its setup state.
- [ ] Ensure assertions never print API keys, authorization headers, or sensitive
  response bodies.

### 4. Safe Newman runner

- [x] Add a local documented Newman command for the read-only smoke subset.
- [ ] Materialize environment values only in ephemeral files or process
  environment variables.
- [x] Add JUnit output and sanitized CLI summaries.
- [ ] Define deterministic service readiness, timeouts, and retry policy.
- [ ] Run the smoke subset against LOCAL before any remote target.

### 5. Integration fixtures

- [x] Define synthetic setup data and ownership for employers, contracts, and
  templates; JSON validation imports are covered, while committing imports and
  asynchronous exports remain pending.
- [x] Add cleanup steps and verify cleanup success in the guarded local runner.
- [x] Isolate integration data from developer and production data through unique
  identifiers and a loopback-only target guard.
- [ ] Document file fixtures and request ordering dependencies.

### 6. CI and release gates

- [x] Add a workflow for coverage validation and safe smoke execution.
- [x] Add a manual disposable LOCAL integration workflow with database reset cleanup.
- [x] Exclude unstable resource IDs, such as export job status, payroll period, and template IDs, from the default smoke tier.
- [ ] Run it on collection, environment, service contract, and runner changes.
- [x] Add loopback-only expected error contract checks for auth, missing resources, and invalid import payloads.
- [x] Add an explicit HTTPS-only GCP error-contract workflow; remote mutations remain excluded.
- [ ] Keep destructive/provider-refresh workflows manual and target-guarded.
- [ ] Upload JUnit reports without raw payloads or secrets.
- [ ] Define failure ownership and rerun instructions.

### 7. GCP and destructive rollout

- [ ] Obtain explicit approval for each GCP execution tier.
- [ ] Prove the selected requests are read-only or use isolated synthetic data.
- [ ] Add workflow inputs requiring an explicit non-production/production target
  declaration where applicable.
- [ ] Validate rate limits, cost, timeout, and rollback behavior.
- [ ] Record release evidence and close the improvement only after reconciliation.

## Validation gates

- [ ] Collection and environment JSON validation passes.
- [x] Coverage checker passes with no unexplained gaps.
- [x] Newman smoke tests pass against LOCAL.
- [x] Integration fixtures pass with disposable local database reset verification.
- [ ] Destructive tests remain excluded from default CI.
- [ ] Reports contain no secrets, credentials, personal data, payslips, salaries,
  health data, or raw production payloads.
- [ ] Relevant service and Postman documentation is synchronized.
- [ ] Final evidence records commit SHAs, workflow run IDs, target environment,
  request counts, and sanitized conclusions.

## Validation evidence

### Local read-only smoke — 2026-10-25

- Target: local `pf-rates` and `pf-svc-income`; `pf-sheets` is excluded by default because its committed URL is external.
- Database: local PostgreSQL with base, real, and test-only fixtures.
- Runner: Newman through `scripts/run-postman-smoke.py`.
- Requests selected: 25 read-only local requests.
- Assertions: 134 status, latency, content-type, JSON parse, health-contract, CSV-content, array-shape, object-field, async-status, and domain-shape assertions.
- Failures: 0.
- Report: temporary JUnit report; no credentials or payloads committed.
- Corrections discovered: kept economic-index fixtures scoped to `IPC_CL`,
  added a `UF` exchange rate for payroll validation, and updated the collection's local payroll fixture
  variable from stale ID `1` to `527`.

### Local JSON import validation — 2026-10-25

- Target: local `pf-svc-income` with local `pf-rates` and PostgreSQL fixtures.
- Request: `POST /payroll/import/json` with `mode=validate`.
- Result: HTTP `200`.
- Payroll count before/after: `25 → 25`; no data persisted.
- No GCP, Neon, or production target was contacted.

### Local spreadsheet validation — 2026-10-25

- Target: local `pf-svc-income` only.
- Fixture: temporary XLSX generated from the repository sample fixture.
- Result: HTTP `422` because the fixture employer/contract and derived net-pay
  values do not form a valid committed payroll scenario.
- Payroll count remained `25`; no data persisted.
- Follow-up: create a dedicated valid XLSX fixture for the selected employer and
  contract instead of reusing the stale ACME sample.

### Local mutating integration — 2026-10-25

- Employer create: passed.
- Contract create: passed after correcting employer-scoped overlap validation
  and applying the local database constraint migration.
- Regression coverage: 12 repository tests passed, including an assertion that
  the overlap query includes `employer_id`.
- Template create/update: passed.
- Template deactivation: passed.
- Employer cleanup: blocked because template deactivation is soft-delete and the
  API has no hard-delete operation for the template foreign-key dependency.
- The run did not contact GCP, Neon, or production. The local backup remains
  available for reset/restore.
- The local-only backup/reset wrapper
  `postman/scripts/run-local-integration.sh` executed successfully: the complete
  employer/contract/template workflow passed and the disposable database reset
  completed. Production deletion semantics remain unchanged.

### Stable local PDF fixture — 2026-10-25

- Added `postman/scripts/generate-synthetic-payroll-pdf.py` to generate a
  deterministic text-layer PDF without real payroll data.
- The fixture targets `walmart-chile-v1`, period October 2026, and three mapped
  labels. It is generated into `/tmp`, never committed as a binary artifact.
- Preview and preview → JSON `mode=validate` both pass locally with HTTP 200.

### Local PDF preview — 2026-10-25

- Target: local `pf-svc-income` only.
- Fixture: synthetic PDF generated in `/tmp`; no repository or secret PDFs were
  used.
- Basic unresolved fixture: HTTP `200` with no template match and no persisted data.
- Template-shaped fixture: HTTP `200`, `template_id=walmart-chile-v1`, and three
  resolved rows (`SALARY_BASE`, `INCOME_TAX`, `UNEMPLOYMENT_INSURANCE`).

### Local PDF Preview → JSON validation — 2026-10-25

- Converted the resolved preview into the documented JSON import shape.
- `POST /payroll/import/json` with `mode=validate`: HTTP `200`.
- `validated=true`, `saved=null`, `period_count=1`, `item_count=3`.
- The response contained only a pending UF warning for complementary insurance;
  no data was persisted.

### Local XLSX export → import validation — 2026-10-25

- The local export endpoint returned an XLSX successfully.
- Re-importing that export with `mode=validate` returned HTTP `422` because
  historical contribution and complementary-insurance totals do not match the
  current calculation rules.
- Payroll count remained `25`; no data persisted.
- This is a contract/fixture round-trip gap, not a reason to weaken assertions.

### Local minimal XLSX validation — 2026-10-25

- A minimal synthetic XLSX containing only period, employer, contract kind, and
  `salary_base` passed `POST /payroll/import/spreadsheet` with `mode=validate`.
- Result: HTTP `200`; payroll count remained `25 → 25`.
- This is the valid fixture shape to keep for future integration automation;
  historical exported contribution columns must not be reused as authoritative
  inputs.

The run proves the local read-only tier only and intentionally excludes the external `pf-sheets` Web App. It does not authorize GCP,
production, mutating, destructive, refresh, import, or stop-job execution.

### GCP read-only validation — 2026-10-26

- `pf-db` PR #21 was subsequently merged and deployed after this validation; see
  the migration evidence below. The post-migration PDF validation remains open.
- OpenAPI coverage workflow: [run 40259031635](https://github.com/mrturo-pf/pf-postman/actions/runs/40259031635) passed.
- Read-only Postman smoke workflow: [run 40259103021](https://github.com/mrturo-pf/pf-postman/actions/runs/40259103021) passed.
- GCP error-contract workflow: [run 40259513866](https://github.com/mrturo-pf/pf-postman/actions/runs/40259513866) passed for expected `403`, `404`, and `400/422` cases.
- Target: deployed `pf-rates` and `pf-svc-income` only; no mutations, imports,
  refreshes, deletes, or async job triggers were executed.
- `pf-sheets` remained excluded because its Web App is a separate external target.

### pf-db migration deployment — 2026-10-26

- PR #21 (`0021_reapply_income_summary_view_grants.py`) merged successfully:
  commit `44491802c1e3cef2f3db2a9f3876103349cbf1`.
- Neon migration deployment workflow [run 40261211424](https://github.com/mrturo-pf/pf-db/actions/runs/40261211424) passed.
- Documentation workflow [run 40261211372](https://github.com/mrturo-pf/pf-db/actions/runs/40261211372) passed.
- Remaining validation: rerun the GCP synthetic PDF flow and reconcile the runtime
  role/grant evidence.

### GCP post-migration PDF → JSON validation — 2026-10-28

- Workflow: [run 40618005125](https://github.com/mrturo-pf/pf-postman/actions/runs/40618005125).
- Target: configured deployed `pf-svc-income` HTTPS URL; synthetic PDF only.
- PDF generation and preview setup completed, but JSON validation returned HTTP
  `500` before the `validated=true` and `saved=null` assertions.
- No successful post-migration proof of `INC_MV_PAY_SUMMARY` runtime access was
  obtained. No payloads, credentials, or sensitive artifacts were uploaded.
- Follow-up remains limited to inspecting/reconciling the deployed runtime role
  and grants, then rerunning this workflow; no additional merge is required.

### GCP runtime grant diagnosis — 2026-10-28

- Cloud Run service `pf-svc-income` is running revision `pf-svc-income-00004-pcs`
  with service account `pf-svc-income@coreassistant-474022.iam.gserviceaccount.com`.
- The runtime database secret is configured for PostgreSQL role `pf_payroll_app`;
  the secret value itself was not recorded.
- Sanitized Cloud Run logs identify the failing operation as
  `REFRESH MATERIALIZED VIEW "INC_MV_PAY_SUMMARY"` with
  `asyncpg.exceptions.InsufficientPrivilegeError`.
- Migration `0021` grants `SELECT` on the materialized view, but PostgreSQL
  requires object ownership (or an explicitly controlled `SECURITY DEFINER`
  operation) for `REFRESH MATERIALIZED VIEW`. Therefore the migration deploy is
  confirmed, but it cannot by itself authorize this runtime refresh.
- Do not grant the runtime role ownership as an unreviewed workaround. The
  service/database owners must choose a least-privilege design, then rerun the
  GCP validation.
- Disposable PostgreSQL 16 validation passed locally: upgraded through `0020`,
  created a disposable `pf_payroll_app` role with `SELECT` on `INC_PAYROLL`,
  applied `0021` and `0022`, verified the function owner/grants, confirmed the
  runtime role's direct `REFRESH MATERIALIZED VIEW` was rejected with
  `must be owner`, confirmed `SELECT public."INC_FN_REFRESH_PAY_SUMMARY"()`
  succeeded, and downgraded `0022` back to `0021` with the function removed.
- `pf-db` PR #22 and `pf-svc-income` PR #14 were merged and deployed
  successfully. The Neon migration deploy passed in run `40620797261`; the
  Cloud Run deploy passed in run `40620835077`, with traffic on revision
  `pf-svc-income-00005-b9g`.
- Post-deploy GCP rerun [run 40621978307](https://github.com/mrturo-pf/pf-postman/actions/runs/40621978307)
  reached the new service. PDF preview returned HTTP 200 with the synthetic
  template and three rows, but JSON validation returned HTTP 502 because the
  service called `pf-rates` without `PF_RATES_API_KEY` and received HTTP 403 for
  the UF exchange-rate request.
- Root cause: the shared `pf-common` reusable deploy workflow only injected
  `PF_RATES_API_KEY` for the legacy `pf-payroll` name, while the current caller
  is `pf-svc-income`. Fix [PR #17](https://github.com/mrturo-pf/pf-common/pull/17),
  commit `9c4cdd6`, was merged as `c5f11eee`.
- The redeployed service revision `pf-svc-income-00006-727` contains the
  `PF_RATES_API_KEY` Secret Manager reference and receives 100% traffic.
- Final GCP PDF → JSON validation [run 40623037144](https://github.com/mrturo-pf/pf-postman/actions/runs/40623037144)
  passed: synthetic preview resolved `walmart-chile-v1` with 3 rows, and JSON
  validation returned `validated=true`, `saved=null`, and `item_count=3`.
- The same sanitized log inspection found request-debug output containing the
  `x-api-key` header name and value in Cloud Run stdout. The value is not recorded
  here. A redaction fix is open in `pf-svc-income` [PR #15](https://github.com/mrturo-pf/pf-svc-income/pull/15),
  commit `11d84ab`: HTTP 500 responses are generic and the unexpected-error
  handler no longer emits exception tracebacks that can include request scope
  headers. The PR's targeted tests, Ruff, typecheck, dead-code, and duplicate-code
  hooks passed. PR #15 was merged as `9cb463e` and deployed successfully in run
  `40623764482`; traffic is on `pf-svc-income-00007-nqf`.
- API-key rotation was attempted without printing or persisting the generated
  value, but Secret Manager rejected the write with the organization's
  VPC Service Controls policy. The owner explicitly decided to skip rotation
  for this improvement. Neither `PF_INCOME_API_KEY` nor
  `PF_SVC_INCOME_API_KEY_GCP` changed. The residual exposure risk remains
  documented and must not be reported as remediated by IMP-011.

### Newman payroll validation contracts — 2026-10-28

- Workflow: `run-postman-integration-local.yml`.
- Run: [40626637215](https://github.com/mrturo-pf/pf-postman/actions/runs/40626637215).
- Newman executed the synthetic PDF preview, chained PDF → JSON `mode=validate`,
  and minimal XLSX `mode=validate` requests.
- Result: 3 requests, 9 assertions, 0 failures.
- The same run passed the read-only smoke tier with 23 requests, 124 assertions,
  and 0 failures, plus mutation fixtures and disposable database reset cleanup.
- The Newman contract subset passed with 4 requests, 12 assertions, and 0
  failures, including XLSX binary response checks.
- The temporary Newman collection materialized fixture paths without modifying
  committed collection/environment files or persisting payroll data.

### CI LOCAL integration — 2026-10-26

- Workflow: `run-postman-integration-local.yml`.
- Run: [40258479096](https://github.com/mrturo-pf/pf-postman/actions/runs/40258479096).
- OpenAPI coverage, local error contracts, read-only smoke, mutation fixtures,
  and disposable database reset all passed.

### Local Neon snapshot replica validation — 2026-10-25

- Restored `modules/pf-db/secrets/neon_dump.sql` into a disposable local
  PostgreSQL 16 database after removing only the PostgreSQL 18-only
  `transaction_timeout` setting from a temporary copy.
- Snapshot state verified: Alembic `0020` head, 3 employers, 23 payrolls, and
  1 template.
- Corrected the collection to use `IPC_CL` for economic-index requests; `UF`
  remains represented only as a monetary/exchange-rate unit.
- Adjusted smoke: 25 read-only requests, 106 assertions, 0 failures against the
  restored snapshot; no fixture was inserted into the replica.
- OpenAPI coverage passed.
- PDF preview resolved `walmart-chile-v1` with 3 rows.
- Mutating integration setup passed and the snapshot was restored from a backup
  afterward; template soft-delete still prevents API-only employer cleanup.
- JSON import `mode=validate` passed with a free snapshot period (`WALMART-CHILE`,
  2026-10), returning HTTP 200 without persistence.
- Minimal XLSX import `mode=validate` passed for the same free period, returning
  HTTP 200 without persistence.
- No GCP, Neon, or production mutation was performed; all activity used the local
  restored copy.

## Remaining work before closure

The following work remains intentionally open for the next session. None of it
authorizes production mutation by itself.

### Immediate blockers

- [x] Merge and apply `pf-db` PR #21 (`0021_reapply_income_summary_view_grants.py`).
  PR #21 was merged as `44491802c1e3cef2f3db2a9f3876103349cbf1` on
  2026-10-26, and the Neon migration deploy completed successfully in workflow
  run `40261211424`.
- [x] Merge and deploy the least-privilege refresh remediation (`pf-db` PR #22
  and `pf-svc-income` PR #14). The post-deploy rerun proved the materialized-view
  privilege error no longer occurs.
- [x] Merge `pf-common` PR #17 and redeploy `pf-svc-income` so the active
  revision receives `PF_RATES_API_KEY`; traffic is on `pf-svc-income-00006-727`.
- [x] Re-run the GCP synthetic PDF validation workflow and record
  `template_id=walmart-chile-v1`, `resolved_rows=3`, `validated=true`,
  `saved=null`, and `item_count=3` in run `40623037144`.
- [x] Reconcile the GCP runtime role/grant behavior without recording
  connection strings, credentials, or secret payloads; the dedicated runtime
  role uses the `SECURITY DEFINER` refresh function and does not own the view.

### Assertion coverage

- [x] Execute the PDF Preview, JSON import, and XLSX import assertions through
  Newman in an integration collection/workflow, not only through the direct
  local runner and curl-based local evidence. Run `40626637215` passed with 3
  requests, 9 assertions, and 0 failures.
- [ ] Execute the complete async export lifecycle: trigger, capture `job_id`,
  poll, terminal status, and `file_id`/`error_message` validation. The Postman
  collection now has trigger/status assertions and a documented manual-only
  boundary in commit `c556bfd`; execution remains intentionally outside default
  CI because it starts a Google Drive export.
- [x] Add binary response validation for the supported XLSX export and exact
  CSV column contracts where the collection exposes them. The local Newman run
  `40627503496` passed XLSX binary content-type/body assertions; PDF is an input
  to preview and has no binary download endpoint in `pf-svc-income`, so no output
  PDF contract was invented.
- [ ] Add controlled GCP error-contract execution after the grant blocker is
  resolved; keep expected `401/403`, `404`, `409`, and `400/422` cases separate
  from happy-path smoke.

### `pf-sheets` coverage decision

- [ ] Decide whether `pf-sheets` uses a local Web App mock, a separate external
  read-only workflow, or inventory-only coverage.
- [ ] Document the chosen target, credentials boundary, route inventory, and why
  it is excluded from the main local microservice smoke.

### CI and operations

- [ ] Define automatic trigger policy for collection, environment, OpenAPI,
  service-contract, fixture, and runner changes; the current integration workflow
  is manual by design.
- [ ] Document failure ownership, rerun commands, JUnit artifact retention, and
  fixture-vs-service failure triage.
- [ ] Keep destructive/provider-refresh execution behind explicit manual inputs,
  target guards, bounded timeouts, and cleanup/restore evidence.
- [ ] Record final commit SHAs, workflow run IDs, target environments, request and
  assertion counts, sanitized failures, and unresolved limitations.

### Closure gate

- [ ] Update Issue #35 and the GitHub Project after the remaining evidence is
  reconciled.
- [ ] Move `IMP-011` through the approved lifecycle to `Released`/`Closed` only
  after the GCP, `pf-sheets`, CI-trigger, and evidence decisions are complete.

## Rollback and failure handling

- Disable the new workflow or revert its workflow/runner commit without changing
  service endpoints.
- Preserve collection and environment sync independently from test execution.
- Quarantine failed fixture data using the documented cleanup procedure.
- Do not retry destructive or provider-refresh requests automatically after an
  ambiguous timeout.
- Escalate security, privacy, data-loss, or production-safety findings immediately.

## Ownership

- `pf-postman`: collection structure, assertions, Newman runner, reports, and
  Postman workflow.
- `pf-rates` and `pf-svc-income`: OpenAPI truth, endpoint semantics, service test
  fixtures, and compatibility validation.
- `pf-sheets`: Web App route inventory and service-specific contract evidence when
  included.
- `pf-improvements`: coordination record, decision artifacts, plan, and sanitized
  release evidence.
