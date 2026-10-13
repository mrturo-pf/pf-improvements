# Plan: ecosystem HTTP error baseline

Date: 2026-10-12
Status: investigating
Level: M
Scope: Reusable HTTP error classification and evidence baseline for `pf-rates`, `pf-payroll`, and `pf-sheets`.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md)
Approved: pending explicit owner approval
Superseded-by: none

## 1. Gates

- [x] Initial evidence boundary and taxonomy drafted.
- [ ] Brief and recommendation approved.
- [ ] Existing service error contracts inventoried.
- [ ] Sanitized evidence template validated against synthetic failures.
- [ ] `pf-rates`, `pf-payroll`, and `pf-sheets` adoption owners confirmed.
- [ ] Release-validation checklist published and linked from affected docs.

## 2. Implementation slices

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
| 2026-10-12 | investigating | Promoted IMP-006 to formal artifacts; no runtime mutation. | Register and current service boundaries |

## 4. Release record

- Commits: pending
- Workflow runs: pending
- Owner approval: pending
- Adoption evidence: pending
