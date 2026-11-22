# Brief: backend request correlation ID

Date: 2026-11-22  
Status: observation  
Level: M  
Scope: Common request identity for PF backend services and synchronous downstream calls.  
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: design preparation by `a0a11b7`  
Superseded-by: none

## Objective

Give every backend request a stable correlation identifier that is visible in logs
from all involved services. A caller may send `X-Request-ID`; when it does not, the
first backend service generates one. The effective identifier is then retained for
the complete request and propagated to downstream PF backend calls.

## In-scope services and boundaries

- `pf-svc-reference` FastAPI request boundary and structured logs;
- `pf-svc-income` FastAPI request boundary and structured logs;
- `pf-svc-income` HTTP calls to `pf-svc-reference`;
- API documentation, Postman examples, unit tests, and integration tests;
- a common header/value/log-field contract that future `pf-svc-*` services can adopt.

## Proposed contract

```text
Request header:  X-Request-ID
Format:         lowercase canonical UUIDv4
Log field:      request_id
Response:       echo effective X-Request-ID
Missing:        generate at first backend boundary
```

Example:

```text
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

## Non-objectives

- No distributed tracing platform or paid observability product;
- no database-backed sequence or globally incrementing integer;
- no change to API-key authentication;
- no logging of request bodies, credentials, payroll data, or personal data;
- no requirement for external callers to generate an ID before using the API;
- no silent creation of a new ID during retries or downstream calls.

## Acceptance criteria

1. Every request handled by either backend has exactly one effective `request_id`.
2. Missing IDs are generated; valid IDs are preserved; malformed/oversized values are
   handled by the approved validation policy and never injected into logs.
3. The effective ID is present in structured log events for request start, completion,
   and handled error paths.
4. `pf-svc-income` forwards the same ID to `pf-svc-reference`, including retries.
5. Responses expose the effective ID in `X-Request-ID`.
6. The same format and semantics are documented for future `pf-svc-*` services.
7. Existing clients that omit the header remain compatible.
8. Tests cover both services, propagation, retries, errors, and cleanup between requests.
9. Documentation and Postman examples are synchronized without adding secrets.
