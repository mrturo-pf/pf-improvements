# Recommendation: backend request correlation ID

Date: 2026-11-22  
Status: observation  
Level: M  
Scope: FastAPI middleware, structured logging, backend HTTP propagation, and API contracts.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)  
Approved: design preparation by `a0a11b7`  
Superseded-by: none

## 1. Executive recommendation

Adopt `X-Request-ID` as the ecosystem-wide correlation header and use a canonical
lowercase UUIDv4 value. Implement the behavior at the HTTP adapter boundary of each
`pf-svc-*` backend and bind the value to `structlog` request context for the entire
request lifetime.

The effective ID is generated when absent, returned in the response, and forwarded
unchanged by every synchronous backend client. This gives callers a useful ID without
forcing existing integrations to change before adoption.

## 2. Why UUIDv4 instead of a numeric sequence

A shared numeric counter would require coordination, persistence, and concurrency
handling, while revealing request volume. UUIDv4 is globally unique enough for log
correlation, works across independently scaled Cloud Run instances, and introduces no
paid or always-on infrastructure. "Correlativo" should mean correlation, not a
predictable public sequence.

## 3. Validation policy

The implementation should accept canonical UUIDv4 values only. For a missing header,
generate a new value. For malformed or oversized values, return `400 Bad Request`
without logging or echoing the raw value. This makes the common format enforceable
while preserving compatibility for clients that omit the header.

The header should be capped at 64 characters and the value should be bound as the
structured field `request_id`. Do not use the ID as an authorization or data-access
credential.

## 4. Request context design

Use `structlog.contextvars` (or the service's equivalent context mechanism) in a small
middleware component:

- clear stale context before binding;
- bind `request_id` once;
- log sanitized request completion metadata and status;
- set the response header;
- clear context in `finally`, including cancellation and exception paths.

The middleware must be added consistently to both services and tested for context
leakage when the same worker handles sequential requests.

## 5. Downstream propagation

Update the `pf-svc-income` HTTP client to read the request-scoped ID and add
`X-Request-ID` to its existing `X-API-Key` headers. Retries reuse the same header.
`pf-svc-reference` applies the same inbound middleware, so its logs automatically join
the originating request. Future backend clients must follow the same adapter contract.

If a backend call can occur outside an inbound request, the client should generate a
local ID at that boundary and bind/log it rather than sending an empty header. This
case must be explicit and tested, not handled by a silent global fallback.

## 6. Rejected alternatives

- Numeric database-backed request sequence: unnecessary state, predictable, and not
  safe as a distributed correlation mechanism.
- A new paid tracing platform: conflicts with the ecosystem cost priority before the
  lightweight contract is proven.
- Generating a new ID in every service: breaks cross-service joins.
- Logging only at the endpoint handler: misses middleware/dependency/error events.
- Accepting arbitrary header text: creates log-injection and response-header risks.
- Requiring all existing clients to add the header immediately: avoidable compatibility
  break because the backend can generate it.

## 7. Compatibility impact

This is an additive HTTP behavior when the header is omitted and a generated ID is
returned. A present malformed or oversized header introduces a documented `400` contract;
existing valid request/response bodies, authentication, and routes remain unchanged.
The `X-Request-ID` contract must be added to API docs and representative Postman requests
so the behavior is discoverable.
