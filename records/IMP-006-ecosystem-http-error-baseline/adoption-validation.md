# IMP-006 Adoption Validation

Date: 2026-10-13
Mode: synthetic dry run
Production calls: none
Runtime/API changes: none

This document records the final adoption dry run for `pf-rates`, `pf-payroll`, and
`pf-sheets`. Each case uses the sanitized evidence template and reuses synthetic
fixtures from `synthetic-validation.md`; no production payloads or credentials were
collected.

## Adoption matrix

| Service | Synthetic case | Classification | Owner | Result |
|---|---|---|---|---|
| `pf-rates` | `SYN-004` provider timeout on `GET /exchange-rates/value` | `dependency` | `pf-rates` | Passed |
| `pf-payroll` | `SYN-002` invalid `POST /payroll/import/json` input | `client/input` | `pf-payroll` | Passed |
| `pf-sheets` | `SYN-006` unknown `doPost` Web App failure | `unknown` | `pf-sheets` | Passed |

## pf-rates dry run

```yaml
record_id: SYN-004
service: pf-rates
boundary: external-provider
route_or_event: "GET /exchange-rates/value"
http_status: 503
error_code: market_data_provider_timeout
classification: dependency
dependency: mindicador
retry_behavior: exhausted
owner: pf-rates
next_action: Verify retry/backoff behavior and preserve a safe dependency error.
resolution: validated
```

Checks passed:

- dependency is named;
- timeout and retry behavior are recorded;
- no provider payload or secret is present;
- the public response contract is not changed.

## pf-payroll dry run

```yaml
record_id: SYN-002
service: pf-payroll
boundary: http
route_or_event: "POST /payroll/import/json"
http_status: 422
error_code: request_validation_failed
classification: client/input
dependency: none
retry_behavior: not_applicable
owner: pf-payroll
next_action: Preserve the validation response and correct the consumer fixture.
resolution: validated
```

Checks passed:

- invalid input is separated from domain failure;
- request field names are recorded without values;
- response metadata is safe;
- no payslip, salary, RUT, or payroll payload is present.

## pf-sheets dry run

```yaml
record_id: SYN-006
service: pf-sheets
boundary: apps-script-webapp
http_status: 500
error_code: unknown
classification: unknown
dependency: unknown
retry_behavior: unknown
owner: pf-sheets
next_action: Collect a safe correlation/timestamp/deployment signal before classifying.
resolution: validated
```

Checks passed:

- `unknown` remains valid when evidence is insufficient;
- no status-only inference promotes the case to another class;
- query parameter names are recorded without the API key or values;
- Apps Script response behavior is not modified.

## Final adoption result

```text
pf-rates:   passed — dependency case
pf-payroll: passed — client/input case
pf-sheets:  passed — unknown/evidence-gap case
```

The baseline is adopted as a documentation and validation process. This does not
authorize public error-contract changes, production mutations, or deployment.
