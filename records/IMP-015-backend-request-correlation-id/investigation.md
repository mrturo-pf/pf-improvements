# Investigation: backend request correlation ID

Date: 2026-11-22  
Status: completed  
Level: M  
Scope: `pf-svc-reference`, `pf-svc-income`, backend-to-backend HTTP calls, structured logs, and API documentation.  
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: investigation and design preparation by `mrturo`
Superseded-by: none

## 1. Current runtime shape

The PF backend services are FastAPI applications with structured logging through
`structlog`:

- `pf-svc-reference` exposes its API from `rates.interfaces.api.main` and creates
  `structlog` loggers in the service and infrastructure layers.
- `pf-svc-income` exposes its API from `payroll.interfaces.api.main` and calls the
  reference service through `payroll.infrastructure.http._http_client` using `httpx`.
- Both services already have an `X-API-Key` authentication header, but no shared
  request-correlation contract or request-scoped logging context was found.

The existing client currently builds a fixed header set containing `X-API-Key`; the
correlation header must be added without logging or exposing the API key.

## 2. Problem

A request entering `pf-svc-income` and then calling `pf-svc-reference` can produce
logs in two services that cannot be reliably joined. Timestamps and Cloud Run
revision metadata are useful but insufficient when requests overlap or retries occur.
The same identifier must be available in every log event produced during one request,
including dependency calls and error paths.

The requirement that a header "be required" and that it be generated when absent is
interpreted as follows: every request has a correlation ID in its request context;
the client may omit the header, in which case the receiving service creates one.
Requests are not rejected merely because the header was absent.

## 3. Proposed common contract

| Item | Decision |
|---|---|
| Request header | `X-Request-ID` |
| Value format | Canonical UUID version 4, normalized to lowercase; for example `550e8400-e29b-41d4-a716-446655440000` |
| Maximum length | 64 characters |
| Missing header | Generate a UUIDv4 at the first backend boundary |
| Invalid/oversized header | Reject with `400 Bad Request`; never log or echo the raw value |
| Invalid request ID | Generate a separate valid ID for the rejected request context, log only that ID and a reason code, and return it in the error response header |
| Invalid reason codes | `request_id_malformed` or `request_id_too_long` |
| Duplicate/multiple values | Reject duplicate headers and comma-separated values with `400 Bad Request` |
| Response header | Echo the effective `X-Request-ID` so callers can report it |
| Structured log field | `request_id` |
| Propagation | Forward the exact effective value on every backend-to-backend HTTP request |
| Scope | One inbound request and all synchronous downstream calls/retries |
| Log cleanup | Clear request context in a `finally` path |

UUIDv4 is preferred over a sequential numeric ID because it is globally unique across
services, does not reveal traffic volume, and requires no shared counter or database.
The term "correlativo" is treated as correlation identifier, not as a public sequence.

## 4. Candidate implementation boundary

Use one focused FastAPI HTTP middleware per service to:

1. read and validate `X-Request-ID`;
2. generate it when absent;
3. bind `request_id` to `structlog.contextvars` for the request lifetime;
4. add the effective value to the response;
5. clear the context in `finally`.

Update the shared internal HTTP client in `pf-svc-income` to accept or obtain the
request-scoped ID and send it with `X-Request-ID`. The client must preserve the same
ID across retries and must not generate a new value for each outbound attempt.

## 5. Compatibility and security observations

- Existing clients that send only `X-API-Key` remain compatible because the backend
  generates the missing ID.
- A response header is needed for clients to discover a generated ID.
- Header values must be length-limited and UUID-validated before binding to logs or
  returning them. Uppercase UUID input is normalized to lowercase; malformed or oversized
  input receives `400` and is never logged or echoed.
- The middleware should cover health and readiness endpoints by default. Any probe
  exception requires an explicit documented decision and tests.
- The middleware runs before authentication and authorization, so `401` and `403`
  responses carry the request ID; an invalid correlation header takes precedence and
  returns `400`.
- Never include API keys, authorization values, request bodies, payslips, RUTs, salaries,
  or health data in correlation logs.
- Unhandled `500` responses must retain the generated/validated request ID in the
  response header and in the error log event.
- Cloud Run request logs and application logs may have different transports, so the
  application field remains the source of truth for joining service events.
- Before rollout, verify that any gateway/proxy does not overwrite `X-Request-ID` with
  a non-conforming value. If a browser frontend reads the response, configure
  `Access-Control-Expose-Headers: X-Request-ID`; backend-only consumers do not need it.

## 6. Evidence needed during implementation

- Current route/middleware inventory for both services.
- Contract tests for missing/valid headers, uppercase normalization, non-canonical UUID
  forms (no hyphens, braces, `urn:uuid:`), non-v4 UUIDs, duplicate/comma-separated
  values, malformed values, and oversized headers.
- Outbound propagation test from income to a stubbed reference service.
- Retry test proving one ID is preserved across attempts.
- Error-path test proving the ID appears in logs and response headers.
- Sanitized sample logs from both services showing the same `request_id`.
- Updated API docs and Postman examples without committed secrets.
