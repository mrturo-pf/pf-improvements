# IMP-006 Adoption and Release Checklist

Date: 2026-10-13
Owner: `pf-base`
Affected repositories: `pf-rates`, `pf-payroll`, `pf-sheets`
Status: active implementation checklist

## Adoption owners

| Boundary | Adoption owner | Evidence location |
|---|---|---|
| `pf-rates` FastAPI errors and market-data dependencies | `pf-rates` | Service API docs, tests, and release validation |
| `pf-payroll` FastAPI errors and payroll dependencies | `pf-payroll` | Service API docs, tests, and release validation |
| `pf-sheets` Apps Script Web App errors | `pf-sheets` | Web App interface, API docs, and synthetic validation |
| Cross-ecosystem taxonomy and checklist | `pf-base` | This checklist and IMP-006 plan |

Ownership acknowledgment was provided by the owner on 2026-10-13 for the adoption
work. Individual maintainer comments remain optional follow-up; no approval is
inferred for runtime deployment.

## Per-repository adoption

### pf-rates

- [x] Link this baseline from the service API/operational documentation.
- [x] Classify representative contract, client, application, dependency, and
      infrastructure failures with sanitized synthetic evidence.
- [x] Confirm provider/database/IAM failures identify the dependency and retry
      behavior without recording secret values.
- [x] Run the repository's required quality gate.
- [x] Record adoption commit and CI evidence in the Issue.

### pf-payroll

- [x] Link this baseline from the service API/operational documentation.
- [x] Classify representative contract, client, application, dependency, and
      infrastructure failures with sanitized synthetic evidence.
- [x] Confirm payroll calculation and import failures include a safe reproduction
      reference without personal or financial payloads.
- [x] Run the repository's required quality gate.
- [x] Record adoption commit and CI evidence in the Issue.

### pf-sheets

- [x] Link this baseline from the Web App/API documentation.
- [x] Classify `doGet`, `doPost`, unauthorized, missing-parameter, dependency, and
      unknown cases using synthetic evidence.
- [x] Confirm Apps Script response handling distinguishes known errors from unknown
      evidence without exposing Script Properties or payloads.
- [x] Run the repository's required quality gate.
- [x] Record adoption commit and CI evidence in the Issue.

## Quality-gate evidence

| Repository | Adoption commit | Evidence |
|---|---|---|
| `pf-rates` | `5b8eec5` and test fix `22d16b4` | Documentation CI passed; Test & Lint passed in run `38437715887`; no runtime deployment authorized. |
| `pf-payroll` | `adabf40` | Documentation CI passed in run `38456667575`; runtime deployment approval was not granted. |
| `pf-sheets` | `92d726c` | Documentation CI passed in run `38456657444`; runtime deployment approval was not granted. |
| `pf-base` | `850f5d0` / central artifacts | Central validation and language checks passed; Issue #1 updated with adoption evidence. |


- [x] Taxonomy approved in the IMP-006 recommendation.
- [x] Sanitized evidence template validated.
- [x] Synthetic cases cover all six classifications.
- [x] No public error response was changed by IMP-006.
- [x] All adoption owners acknowledge the baseline.
- [x] All affected repositories link the baseline.
- [x] Each affected repository records its quality-gate evidence.
- [x] Final adoption evidence is added to GitHub Issue #1.

## Evidence boundary

Never include credentials, tokens, authorization headers, connection strings, raw
request/response bodies, payslips, RUTs, salaries, health data, raw production logs,
or unsanitized provider payloads. Use metadata, stable codes, timestamps, status,
revision/run IDs, synthetic fixtures, and links to restricted evidence locations.
