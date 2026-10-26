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
- [ ] Run it on collection, environment, service contract, and runner changes.
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
- Assertions: 130 status, latency, content-type, JSON parse, health-contract, CSV-content, array-shape, object-field, and async-status assertions.
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
