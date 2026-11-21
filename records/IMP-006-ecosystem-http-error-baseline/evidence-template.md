# IMP-006 Sanitized Error Evidence Template

Use this template for synthetic or approved operational evidence. One record describes
one observed failure or one representative failure class. Keep the record small enough
to review and safe enough to publish.

## Record

```yaml
record_id: ERR-YYYYMMDD-NNN
observed_at: YYYY-MM-DDThh:mm:ssZ
service: pf-rates | pf-payroll | pf-sheets
boundary: http | apps-script-webapp | database | cloud-run | external-provider
route_or_event: <HTTP method and path, Web App operation, or sanitized event name>
http_status: <integer or null when not HTTP>
error_code: <stable application/provider code or unknown>
classification: contract | client/input | application/domain | dependency | infrastructure | unknown
dependency: <service/provider/database/IAM component or none>
correlation_id: <safe identifier or unavailable>
impact: none | low | medium | high | critical
request_metadata:
  query_keys: [<names only>]
  body_fields: [<names only>]
  content_type: <value or none>
  payload: never include
response_metadata:
  content_type: <value or none>
  response_fields: [<names only>]
  body: never include raw body
retry_behavior: none | not_applicable | attempted | exhausted | unknown
evidence_source: synthetic-test | route/OpenAPI | API-docs | Postman | sanitized-log | approved-incident-record
reproduction: <test name, command shape, or concise safe steps>
owner: <repository/team/role>
next_action: <smallest useful next step>
resolution: pending | validated | released | superseded | closed
related_artifacts:
  - <Issue URL or canonical artifact URL>
```

## Classification guidance

| Classification | Use when | Minimum evidence |
|---|---|---|
| `contract` | Route, method, auth, schema, or documented status differs | Route/OpenAPI/API-docs/Postman comparison and sanitized response metadata |
| `client/input` | Caller input is invalid or consumer behavior is unsupported | Field names, validation code, stable status/error code, no payload values |
| `application/domain` | Domain or orchestration behavior is defective | Correlation ID, route, stable error, test/reproduction, owner |
| `dependency` | Database, `pf-rates`, Secret Manager, IAM, or external provider failed | Dependency name, status/timeout, retry behavior, no secret values |
| `infrastructure` | Cloud Run, networking, deployment, capacity, or runtime failed | Revision/run metadata, latency/capacity evidence, no raw logs |
| `unknown` | Evidence is insufficient for a safe classification | Explicit evidence gap and next collection step |

## Redaction rules

Never include:

- API keys, access tokens, cookies, authorization headers, passwords, or connection
  strings;
- full request or response bodies;
- payslips, RUTs, salaries, health information, or other personal/financial data;
- raw production logs or database rows;
- provider payloads that contain more data than the minimum metadata required.

Use field names, counts, status codes, stable error codes, truncated safe identifiers,
revision IDs, workflow run IDs, timestamps, and hashes only when comparison requires
them. If safe redaction is uncertain, record `unknown` and escalate for review.

## Synthetic example

```yaml
record_id: ERR-20261013-001
observed_at: 2026-10-13T17:00:00Z
service: pf-rates
boundary: http
route_or_event: "GET /exchange-rates/value"
http_status: 404
error_code: exchange_rate_not_found
classification: dependency
dependency: market-data-provider
correlation_id: unavailable
impact: low
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
reproduction: "test_get_exchange_rate_value_found_and_not_found"
owner: pf-rates
next_action: Confirm provider availability and preserve the stable 404 contract.
resolution: validated
related_artifacts:
  - https://github.com/mrturo-pf/pf-base/issues/1
```

This example is synthetic. It is not evidence that the provider was unavailable in
production.
