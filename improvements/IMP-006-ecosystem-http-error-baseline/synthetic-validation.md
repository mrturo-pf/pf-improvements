# IMP-006 Synthetic Validation Cases

Date: 2026-10-13
Purpose: Validate the sanitized evidence template against representative failure
classes without calling production services, external providers, or real databases.

All records below are synthetic. The routes, IDs, timestamps, and error codes are
examples for schema validation only.

## Case matrix

| Case | Service | Boundary | HTTP status | Classification | Owner | Expected next action |
|---|---|---|---:|---|---|---|
| `SYN-001` | `pf-rates` | HTTP | 409 | `contract` | `pf-base` | Compare route/OpenAPI/API docs/Postman and decide whether the difference is intentional. |
| `SYN-002` | `pf-payroll` | HTTP | 422 | `client/input` | `pf-payroll` | Return the stable validation contract and correct the consumer input. |
| `SYN-003` | `pf-payroll` | HTTP | 500 | `application/domain` | `pf-payroll` | Reproduce with a synthetic fixture and isolate the failing use-case path. |
| `SYN-004` | `pf-rates` | external-provider | 503 | `dependency` | `pf-rates` | Record provider timeout/retry metadata and verify safe retry behavior. |
| `SYN-005` | `pf-payroll` | cloud-run | 503 | `infrastructure` | `pf-common` | Check revision, capacity, latency, and dependency health without collecting payloads. |
| `SYN-006` | `pf-sheets` | apps-script-webapp | 500 | `unknown` | `pf-sheets` | Collect the next safe evidence point; do not classify from the status alone. |

## Synthetic records

### SYN-001 — Contract mismatch

```yaml
record_id: SYN-001
observed_at: 2026-10-13T17:10:00Z
service: pf-rates
boundary: http
route_or_event: "GET /exchange-rates/value"
http_status: 409
error_code: contract_status_mismatch
classification: contract
dependency: none
correlation_id: syn-contract-001
impact: medium
request_metadata:
  query_keys: [currency_code, rate_date]
  body_fields: []
  content_type: none
  payload: never include
response_metadata:
  content_type: application/json
  response_fields: [detail]
  body: never include raw body
retry_behavior: not_applicable
evidence_source: synthetic-test
reproduction: Compare the documented response matrix with a synthetic 409 response.
owner: pf-base
next_action: Compare route, OpenAPI, API docs, and Postman before changing a contract.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-improvements/blob/main/improvements/IMP-006-ecosystem-http-error-baseline/evidence-template.md
```

### SYN-002 — Invalid client input

```yaml
record_id: SYN-002
observed_at: 2026-10-13T17:11:00Z
service: pf-payroll
boundary: http
route_or_event: "POST /payroll/import/json"
http_status: 422
error_code: request_validation_failed
classification: client/input
dependency: none
correlation_id: syn-client-002
impact: low
request_metadata:
  query_keys: []
  body_fields: [mode, periods]
  content_type: application/json
  payload: never include
response_metadata:
  content_type: application/json
  response_fields: [detail]
  body: never include raw body
retry_behavior: not_applicable
evidence_source: synthetic-test
reproduction: Send a synthetic body with an invalid field shape.
owner: pf-payroll
next_action: Preserve the validation response and correct the consumer fixture.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-payroll/blob/main/docs/api.md
```

### SYN-003 — Application/domain defect

```yaml
record_id: SYN-003
observed_at: 2026-10-13T17:12:00Z
service: pf-payroll
boundary: http
route_or_event: "POST /payroll/import/json"
http_status: 500
error_code: payroll_calculation_error
classification: application/domain
dependency: none
correlation_id: syn-application-003
impact: high
request_metadata:
  query_keys: []
  body_fields: [mode, periods]
  content_type: application/json
  payload: never include
response_metadata:
  content_type: application/json
  response_fields: [detail]
  body: never include raw body
retry_behavior: none
evidence_source: synthetic-test
reproduction: Execute the calculation with a synthetic fixture that triggers the domain branch.
owner: pf-payroll
next_action: Add a focused regression test and isolate the failing use-case path.
resolution: pending
related_artifacts:
  - https://github.com/mrturo-pf/pf-payroll/blob/main/docs/api.md
```

### SYN-004 — External dependency timeout

```yaml
record_id: SYN-004
observed_at: 2026-10-13T17:13:00Z
service: pf-rates
boundary: external-provider
http_status: 503
error_code: market_data_provider_timeout
classification: dependency
dependency: mindicador
correlation_id: syn-dependency-004
impact: medium
request_metadata:
  query_keys: [currency_code, rate_date]
  body_fields: []
  content_type: none
  payload: never include
response_metadata:
  content_type: application/json
  response_fields: [detail]
  body: never include raw body
retry_behavior: exhausted
evidence_source: synthetic-test
reproduction: Use a deterministic provider stub that raises a timeout.
owner: pf-rates
next_action: Verify retry/backoff behavior and preserve a safe dependency error.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-rates/blob/main/docs/api.md
```

### SYN-005 — Infrastructure failure

```yaml
record_id: SYN-005
observed_at: 2026-10-13T17:14:00Z
service: pf-payroll
boundary: cloud-run
http_status: 503
error_code: revision_unavailable
classification: infrastructure
dependency: cloud-run
correlation_id: syn-infrastructure-005
impact: high
request_metadata:
  query_keys: []
  body_fields: []
  content_type: none
  payload: never include
response_metadata:
  content_type: text/plain
  response_fields: []
  body: never include raw body
retry_behavior: attempted
evidence_source: synthetic-test
reproduction: Use synthetic revision/capacity metadata; do not invoke production.
owner: pf-common
next_action: Check revision, capacity, latency, and dependency health.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-common/blob/main/README.md
```

### SYN-006 — Insufficient evidence

```yaml
record_id: SYN-006
observed_at: 2026-10-13T17:15:00Z
service: pf-sheets
boundary: apps-script-webapp
http_status: 500
error_code: unknown
classification: unknown
dependency: unknown
correlation_id: unavailable
impact: medium
request_metadata:
  query_keys: [date, code, key]
  body_fields: []
  content_type: text/plain
  payload: never include
response_metadata:
  content_type: text/plain
  response_fields: []
  body: never include raw body
retry_behavior: unknown
evidence_source: synthetic-test
reproduction: Provide only a synthetic 500 status with no additional evidence.
owner: pf-sheets
next_action: Collect a safe correlation/timestamp/deployment signal before classifying.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-sheets/blob/main/docs/api.md
```

## Validation result

All six classifications are represented, each record has the required sanitized
fields, and no case contains a real payload, credential, production identifier, or
external request. A status code alone never promotes `unknown` to another class.
