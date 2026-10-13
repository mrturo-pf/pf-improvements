# Plan: ecosystem HTTP error baseline

Date: 2026-10-12
Status: validated
Level: M
Scope: Reusable HTTP error classification and evidence baseline for `pf-rates`, `pf-payroll`, and `pf-sheets`.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md)
Approved: 2026-10-13 by owner (conversation)
Superseded-by: none

## 1. Gates

- [x] Initial evidence boundary and taxonomy drafted.
- [x] Brief and recommendation approved.
- [x] Existing service error contracts inventoried.
- [x] Sanitized evidence template validated against synthetic failures.
- [x] Synthetic contract, client, application, dependency, infrastructure, and unknown cases recorded.- [x] `pf-rates`, `pf-payroll`, and `pf-sheets` adoption owners confirmed.
- [x] Release-validation checklist published and linked from affected docs.

## 2. Contract inventory evidence

The initial read-only route and Web App inventory is recorded in
[`contract-inventory.md`](contract-inventory.md). It covers the implemented
`pf-rates` and `pf-payroll` route surfaces, the `pf-sheets` `doGet`/`doPost`
boundary, authentication differences, and the next comparisons against OpenAPI,
API docs, Postman, and consumer behavior.

## 3. Evidence template

The sanitized record schema and synthetic example are defined in
[`evidence-template.md`](evidence-template.md). The schema separates HTTP status,
classification, dependency, owner, next action, and resolution without storing
operational task status in Git.

## 4. Synthetic validation

The six representative synthetic cases are defined and validated in
[`synthetic-validation.md`](synthetic-validation.md). They cover every taxonomy
class without invoking production services or collecting real data.

## 5. Implementation slices
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

## 6. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-10-13 | in progress | Owner approved the brief and recommendation; started Slice 1 contract inventory. | Conversation approval; current service boundaries |
| 2026-10-13 | in progress | Completed Slice 1 initial route/Web App inventory; documented authentication boundaries and next OpenAPI/docs/Postman comparisons. | [`contract-inventory.md`](contract-inventory.md) |
| 2026-10-13 | in progress | Added and validated the sanitized evidence template and synthetic example; no production evidence or runtime mutation. | [`evidence-template.md`](evidence-template.md); synthetic schema assertions |
| 2026-10-13 | in progress | Added six synthetic validation cases covering all taxonomy classes; no production calls or runtime mutation. | [`synthetic-validation.md`](synthetic-validation.md) |
| 2026-10-13 | validated | Completed adoption owner acknowledgment, linked affected service docs, recorded quality-gate evidence, and added final adoption evidence to Issue #1. No runtime deployment authorized. | [`adoption-release-checklist.md`](adoption-release-checklist.md); Issue #1; repository CI runs |

## 7. Release record

- Commits: `850f5d0` central adoption checklist
- Workflow runs: `38437715887`, `38456667575`, `38456657444` — relevant quality/documentation checks passed
- Owner approval: recorded 2026-10-13
- Adoption evidence: complete; no runtime deployment authorized
