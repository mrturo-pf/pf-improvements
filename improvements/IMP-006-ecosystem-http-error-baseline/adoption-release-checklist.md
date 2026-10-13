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

Ownership follows the PF repository map. Explicit maintainer acknowledgment remains
an operational follow-up; this document does not infer approval from ownership.

## Per-repository adoption

### pf-rates

- [ ] Link this baseline from the service API/operational documentation.
- [ ] Classify representative contract, client, application, dependency, and
      infrastructure failures with sanitized synthetic evidence.
- [ ] Confirm provider/database/IAM failures identify the dependency and retry
      behavior without recording secret values.
- [ ] Run the repository's required quality gate.
- [ ] Record adoption commit and CI evidence in the Issue.

### pf-payroll

- [ ] Link this baseline from the service API/operational documentation.
- [ ] Classify representative contract, client, application, dependency, and
      infrastructure failures with sanitized synthetic evidence.
- [ ] Confirm payroll calculation and import failures include a safe reproduction
      reference without personal or financial payloads.
- [ ] Run the repository's required quality gate.
- [ ] Record adoption commit and CI evidence in the Issue.

### pf-sheets

- [ ] Link this baseline from the Web App/API documentation.
- [ ] Classify `doGet`, `doPost`, unauthorized, missing-parameter, dependency, and
      unknown cases using synthetic evidence.
- [ ] Confirm Apps Script response handling distinguishes known errors from unknown
      evidence without exposing Script Properties or payloads.
- [ ] Run the repository's required quality gate.
- [ ] Record adoption commit and CI evidence in the Issue.

## Cross-ecosystem release gate

- [x] Taxonomy approved in the IMP-006 recommendation.
- [x] Sanitized evidence template validated.
- [x] Synthetic cases cover all six classifications.
- [x] No public error response was changed by IMP-006.
- [ ] All adoption owners acknowledge the baseline.
- [ ] All affected repositories link the baseline.
- [ ] Each affected repository records its quality-gate evidence.
- [ ] Final adoption evidence is added to GitHub Issue #1.

## Evidence boundary

Never include credentials, tokens, authorization headers, connection strings, raw
request/response bodies, payslips, RUTs, salaries, health data, raw production logs,
or unsanitized provider payloads. Use metadata, stable codes, timestamps, status,
revision/run IDs, synthetic fixtures, and links to restricted evidence locations.
