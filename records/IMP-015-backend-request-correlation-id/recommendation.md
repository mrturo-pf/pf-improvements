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

## 2. Contract example

```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

The same canonical lowercase UUIDv4 example should be used in API documentation and
Postman examples.

## 3. Why UUIDv4 instead of a numeric sequence

A shared numeric counter would require coordination, persistence, and concurrency
handling, while revealing request volume. UUIDv4 is globally unique enough for log
correlation, works across independently scaled Cloud Run instances, and introduces no
paid or always-on infrastructure. "Correlativo" should mean correlation, not a
predictable public sequence.

## 4. Validation policy

The implementation should accept UUIDv4 values only and normalize valid uppercase
input to canonical lowercase. For a missing header, generate a new value. For malformed
or oversized values, return `400 Bad Request` without logging or echoing the raw value.
Generate a separate valid request ID for that rejected request context, log only the ID
and a reason code (`request_id_malformed` or `request_id_too_long`), and return the generated
ID in the error response header. Duplicate headers and comma-separated values use
`request_id_malformed`. The `400` body must use the service's existing error response
schema with a stable message/code; it must not include the raw invalid value.

The header should be capped at 64 characters and the value should be bound as the
structured field `request_id`. Do not use the ID as an authorization or data-access
credential.

## 5. Request context design

Use `structlog.contextvars` (or the service's equivalent context mechanism) in a small
middleware component applied to normal, health, and readiness endpoints by default:

- clear stale context before binding;
- bind `request_id` once;
- log a request-start event and sanitized request completion metadata/status, including
  unhandled `500` paths;
- set the response header, including generated IDs on rejected requests;
- clear context in `finally`, including cancellation and exception paths.

The middleware must be added consistently to both services, run before authentication
and authorization so `401`/`403` responses carry an ID, and be tested for context leakage
when the same worker handles sequential requests. A malformed correlation header takes
precedence over API-key validation and returns `400`.

## 6. Downstream propagation

Update the `pf-svc-income` HTTP client so each outbound call constructs its headers
from the current request context and adds `X-Request-ID` alongside `X-API-Key`.
The header must be added per call, not stored as one process-wide fixed header set.
Retries reuse the same header value for that call.
`pf-svc-reference` applies the same inbound middleware, so its logs automatically join
the originating request. Future backend clients must follow the same adapter contract.

If a backend call can occur outside an inbound request, the client should generate a
local ID at that boundary and bind/log it rather than sending an empty header. This
case must be explicit and tested, not handled by a silent global fallback. Before rollout,
verify that any gateway/proxy preserves the contract and does not overwrite the header;
if a browser frontend consumes responses, expose it through CORS.

## 7. Rejected alternatives

- Numeric database-backed request sequence: unnecessary state, predictable, and not
  safe as a distributed correlation mechanism.
- A new paid tracing platform: conflicts with the ecosystem cost priority before the
  lightweight contract is proven.
- Generating a new ID in every service: breaks cross-service joins.
- Logging only at the endpoint handler: misses middleware/dependency/error events.
- Accepting arbitrary header text: creates log-injection and response-header risks.
- Requiring all existing clients to add the header immediately: avoidable compatibility
  break because the backend can generate it.

## 8. Compatibility impact

This is an additive HTTP behavior when the header is omitted and a generated ID is
returned. A present malformed or oversized header introduces a documented `400` contract;
existing valid request/response bodies, authentication, and routes remain unchanged.
The `X-Request-ID` contract must be added to API docs and representative Postman requests
so the behavior is discoverable.
