# Plan: ecosystem HTTP error baseline

Date: 2026-10-12
Status: in progress
Level: M
Scope: Reusable HTTP error classification and evidence baseline for `pf-rates`, `pf-payroll`, and `pf-sheets`.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md)
Approved: 2026-10-13 by owner (conversation)
Superseded-by: none

## 1. Gates

- [x] Initial evidence boundary and taxonomy drafted.
- [x] Brief and recommendation approved.
- [x] Existing service error contracts inventoried.
- [ ] Sanitized evidence template validated against synthetic failures.
- [ ] `pf-rates`, `pf-payroll`, and `pf-sheets` adoption owners confirmed.
- [ ] Release-validation checklist published and linked from affected docs.

## 2. Contract inventory evidence

The initial read-only route and Web App inventory is recorded in
[`contract-inventory.md`](contract-inventory.md). It covers the implemented
`pf-rates` and `pf-payroll` route surfaces, the `pf-sheets` `doGet`/`doPost`
boundary, authentication differences, and the next comparisons against OpenAPI,
API docs, Postman, and consumer behavior.

## 3. Implementation slices
### Slice 1 — Contract inventory

Compare routes, OpenAPI, service API docs, Postman, and Apps Script Web App
interfaces. Record intentional differences separately from defects.

### Slice 2 — Evidence template

Define the minimum sanitized record: timestamp, service, route/event, status,
correlation ID, stable error code, class, dependency, impact, evidence source,
owner, and next action.

### Slice 3 — Synthetic validation

Exercise representative contract, client, application, dependency, timeout, and
unknown cases without real personal or financial data.

### Slice 4 — Adoption and release gate

Link the baseline from affected service docs and use it during `pf-svc-income`
release validation. Do not alter public responses as part of this improvement.

## 3. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-10-13 | in progress | Completed Slice 1 initial route/Web App inventory; documented authentication boundaries and next OpenAPI/docs/Postman comparisons. | [`contract-inventory.md`](contract-inventory.md) |

## 4. Release record

- Commits: pending
- Workflow runs: pending
- Owner approval: pending
- Adoption evidence: pending
