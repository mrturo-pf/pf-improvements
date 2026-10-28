# Investigation: API endpoint coverage and Postman automation

Date: 2026-10-25
Status: released
Level: L
Scope: Automated API endpoint coverage, Postman/Newman execution, and safe validation across `pf-postman`, `pf-rates`, `pf-svc-income`, and the applicable `pf-sheets` HTTP surface.
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)
Related Issue: [#35](https://github.com/mrturo-pf/pf-base/issues/35)
Approved: 2026-10-28 by a0a11b7 (explicit authorization)
Superseded-by: none

## Question

How can the PF ecosystem execute and validate all relevant API requests
automatically so that endpoint regressions or missing Postman coverage do not
depend on manually running requests one by one?

## Observed current state

- `pf-postman` contains one canonical collection and LOCAL/GCP environments.
- The collection currently contains 52 requests across `pf-rates`,
  `pf-svc-income`, and `pf-sheets`.
- The repository workflow validates JSON and synchronizes assets to Postman, but
  it does not execute the requests against a service.
- Only a small subset of requests currently contains explicit Postman test
  scripts; JSON validity is not endpoint behavior validation.
- Requests include read-only operations, imports, refreshes, creates, updates,
  deletes, and asynchronous jobs. A blind full-collection run could mutate data,
  call external providers, or depend on state created by another request.
- At least one request is intentionally chained: payroll PDF preview produces
  state consumed by the subsequent JSON import request.
- The service repositories own implementation and API contracts. `pf-postman`
  owns the request catalog and environments; it must not become a second source
  of API behavior.

## Evidence boundary

This investigation uses repository files and sanitized collection metadata only.
No API keys, authorization headers, connection strings, production payloads,
payslips, salaries, personal data, or health data are recorded here.

## Risks and unknowns

1. The complete set of executable endpoints must be derived from the owning
   services' OpenAPI/route definitions, not inferred only from Postman folders.
2. Some operations need deterministic fixtures, setup, cleanup, or ordering.
3. Production/GCP execution must not perform destructive operations by default.
4. `pf-sheets` has a Google Apps Script Web App surface and may need a separate
   contract inventory rather than Newman execution.
5. A generic status-code assertion is insufficient for CSV, binary, async-job,
   and domain-specific response contracts.
6. The runtime environment, database state, external provider availability, and
   file fixtures must be defined before CI execution is enabled.

## Initial findings

The least risky design is layered:

- an OpenAPI-to-Postman coverage check to detect missing or stale requests;
- deterministic Postman assertions for status, response shape, content type, and
  bounded latency;
- Newman smoke execution for safe read-only requests;
- isolated integration execution for mutating workflows with synthetic data;
- explicitly triggered destructive tests with cleanup and a separate approval
  boundary.

A single unclassified collection run is not an acceptable replacement for those
layers.

## Questions for design

- Which requests are safe for every LOCAL run?
- Which fixtures and cleanup operations are required for each mutating workflow?
- Should OpenAPI coverage include only public routes or also operational/admin
  routes?
- How should `pf-sheets` Web App routes be represented in the inventory?
- Which GCP smoke requests are safe, and what rate/latency limits apply?
- Where should JUnit and human-readable reports be retained?
- Which checks must block a pull request versus run only after merge?
