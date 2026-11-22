# Plan: backend request correlation ID

Date: 2026-11-22  
Status: proposed  
Level: M  
Scope: `pf-svc-reference`, `pf-svc-income`, shared HTTP conventions, and API evidence.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: design preparation only by `a0a11b7`; implementation requires a follow-up authorization  
Superseded-by: none

## 1. Gates before implementation

- [ ] Confirm `X-Request-ID` and canonical lowercase UUIDv4 as the final contract.
- [x] Reject malformed or oversized `X-Request-ID` values with `400 Bad Request`
      without logging or echoing the raw value; generate only when the header is absent.
- [ ] Confirm whether health/readiness endpoints participate in the same middleware.
- [ ] Inventory all outbound HTTP paths in both services and identify any calls made
      outside an inbound request context.
- [ ] Confirm the log field name `request_id` and structured-log search examples.

## 2. Shared contract and implementation

- [ ] Add a small request-correlation utility with generation and validation rules.
- [ ] Add request middleware to `pf-svc-reference`.
- [ ] Add request middleware to `pf-svc-income`.
- [ ] Bind the effective ID through `structlog.contextvars` for the full request.
- [ ] Return the effective ID as `X-Request-ID` on successful and error responses.
- [ ] Clear request context in `finally` paths to prevent worker leakage.
- [ ] Update the `pf-svc-income` HTTP client to forward the same ID to
      `pf-svc-reference` and preserve it across retries.
- [ ] Define behavior for outbound calls with no inbound request context.

## 3. Tests and acceptance evidence

- [ ] Unit-test UUID generation and canonical validation.
- [ ] Test missing and valid headers, plus `400` responses for malformed and oversized
      headers without logging or echoing their raw values.
- [ ] Test response-header echoing on success and handled errors.
- [ ] Test request-context cleanup across sequential requests in one worker.
- [ ] Test income-to-reference propagation with a stubbed HTTP server.
- [ ] Test that retries reuse one ID rather than generating per attempt.
- [ ] Test exception/cancellation paths for context cleanup and logging metadata.
- [ ] Capture sanitized evidence showing identical `request_id` values in both services.

## 4. Contract and documentation synchronization

- [ ] Update both services' `docs/api.md` and deployment/operations documentation.
- [ ] Add the header to OpenAPI where appropriate without making it a hard client
      requirement when omission is intentionally supported.
- [ ] Update the shared Postman collection with a generated/static example value,
      never a secret.
- [ ] Document Cloud Logging queries using `jsonPayload.request_id` or the actual
      emitted structlog field shape.
- [ ] Add an adoption note for future `pf-svc-*` services.

## 5. Rollout order

1. Implement and test the common contract in `pf-svc-reference`.
2. Implement the same contract in `pf-svc-income` and its outbound client.
3. Run local API and integration tests with synthetic data.
4. Deploy reference service and validate response/log correlation.
5. Deploy income service and validate an end-to-end request across both services.
6. Monitor error rates and log completeness; rollback only the middleware/client
   changes if a compatibility regression appears.

No database migration, Cloud Run resource, paid monitoring product, or secret change is
expected.

## 6. Rollback

Rollback is a service deployment rollback to the prior revisions. Existing clients
remain compatible because the request header is additive and missing values are
created by the service. Do not remove the documented field from logs until all active
revisions are confirmed rolled back or upgraded.

## 7. Completion evidence

The improvement is complete when both services emit and propagate the same validated
ID for a synthetic end-to-end request, the response exposes `X-Request-ID`, tests pass
for missing/invalid/retry/error paths, docs/Postman are synchronized, and no secrets or
sensitive payloads appear in evidence.
