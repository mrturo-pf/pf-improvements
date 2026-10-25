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

- [ ] Confirm the current request count, folder boundaries, dependencies, and
  intentional exclusions.
- [ ] Export normalized OpenAPI route inventories from `pf-rates` and
  `pf-svc-income` without secrets or live payloads.
- [ ] Define the sanitized `pf-sheets` Web App route inventory, if included.
- [ ] Record all current gaps and stale requests in the Issue and validation
  evidence, not in a second manual register.

### 2. Coverage checker

- [ ] Implement a deterministic method/path comparison tool in the owning
  repository (`pf-postman` unless the service contract requires an adapter).
- [ ] Normalize path parameters, trailing slashes, and documented exclusions.
- [ ] Fail on missing, stale, or duplicate mappings.
- [ ] Add fixtures for valid coverage, intentional exclusion, duplicate request,
  and stale path cases.

### 3. Request assertions

- [ ] Add reusable status and response-time assertions where appropriate.
- [ ] Add JSON, CSV, binary, and async-job assertion helpers without forcing one
  response model onto every endpoint.
- [ ] Add endpoint-specific required-field and invariant assertions.
- [ ] Preserve chained Preview → Import behavior and assert its setup state.
- [ ] Ensure assertions never print API keys, authorization headers, or sensitive
  response bodies.

### 4. Safe Newman runner

- [ ] Add a local documented Newman command for the read-only smoke subset.
- [ ] Materialize environment values only in ephemeral files or process
  environment variables.
- [ ] Add JUnit output and sanitized CLI summaries.
- [ ] Define deterministic service readiness, timeouts, and retry policy.
- [ ] Run the smoke subset against LOCAL before any remote target.

### 5. Integration fixtures

- [ ] Define synthetic setup data and ownership for imports, employers,
  contracts, templates, and asynchronous exports.
- [ ] Add cleanup steps and verify cleanup success.
- [ ] Isolate integration data from developer and production data.
- [ ] Document file fixtures and request ordering dependencies.

### 6. CI and release gates

- [ ] Add a workflow for coverage validation and safe smoke execution.
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
- [ ] Coverage checker passes with no unexplained gaps.
- [ ] Newman smoke tests pass against LOCAL.
- [ ] Integration fixtures pass with cleanup verification.
- [ ] Destructive tests remain excluded from default CI.
- [ ] Reports contain no secrets, credentials, personal data, payslips, salaries,
  health data, or raw production payloads.
- [ ] Relevant service and Postman documentation is synchronized.
- [ ] Final evidence records commit SHAs, workflow run IDs, target environment,
  request counts, and sanitized conclusions.

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
