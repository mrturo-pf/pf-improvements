# Plan: backend request correlation ID

Date: 2026-11-22  
Status: proposed  
Level: M  
Scope: `pf-svc-reference`, `pf-svc-income`, shared HTTP conventions, and API evidence.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: design preparation only by `a0a11b7`; implementation requires a follow-up authorization  
Superseded-by: none

## 1. Gates before implementation

- [x] Confirm `X-Request-ID` and canonical lowercase UUIDv4 as the final contract;
      valid uppercase UUID input is normalized to lowercase.
- [x] Reject malformed or oversized `X-Request-ID` values with `400 Bad Request`
      without logging or echoing the raw value; generate a separate valid request ID
      for the rejected request context and return that ID in the error response header.
- [x] Apply the same middleware to health/readiness endpoints by default; any exception
      requires an explicit documented decision.
- [ ] Inventory all outbound HTTP paths in both services and identify any calls made
      outside an inbound request context.
- [x] Confirm the log field name `request_id`; document structured-log search examples
      during implementation.

## 2. Shared contract and implementation

- [ ] Add a small request-correlation utility with generation and validation rules.
- [ ] Add request middleware to `pf-svc-reference`.
- [ ] Add request middleware to `pf-svc-income`.
- [ ] Bind the effective ID through `structlog.contextvars` for the full request.
- [ ] Run correlation middleware outside authentication/authorization so `401` and
      `403` responses also carry an ID; an invalid correlation header takes precedence
      and returns `400` before API-key validation.
- [ ] Return the effective ID as `X-Request-ID` on successful, handled-error, and
      unhandled-`500` responses, including generated IDs for rejected invalid-header
      requests.
- [ ] Clear request context in `finally` paths to prevent worker leakage.
- [ ] Update the `pf-svc-income` HTTP client to construct headers per outbound call,
      forward the same ID to `pf-svc-reference`, and preserve it across retries.
- [ ] Implement and test outbound calls with no inbound request context: generate one
      local ID at that operation boundary and do not silently create one per retry.

## 3. Tests and acceptance evidence

- [ ] Unit-test UUID generation and canonical validation, including rejection of
      no-hyphen UUIDs, braced UUIDs, `urn:uuid:` values, and non-v4 UUIDs; validate with
      the canonical 8-4-4-4-12 shape and UUID version 4.
- [ ] Test missing and valid headers, uppercase normalization, duplicate headers, and
      comma-separated values, plus `400` responses for malformed and oversized headers
      without logging or echoing their raw values; assert a generated error-context ID
      and reason code are returned.
- [ ] Test response-header echoing on success and handled errors.
- [ ] Test that `401`/`403` responses carry `X-Request-ID`, and that an invalid
      correlation header with an invalid API key returns `400`.
- [ ] Test request-context cleanup across sequential requests in one worker.
- [ ] Test income-to-reference propagation with a stubbed HTTP server.
- [ ] Test that retries reuse one ID rather than generating per attempt.
- [ ] Test exception/cancellation paths for context cleanup, logging metadata, and
      request ID headers on unhandled `500` responses.
- [ ] Test that request-start and request-completion events share the same
      `request_id`.
- [ ] Capture sanitized evidence showing identical `request_id` values in both services.

## 4. Contract and documentation synchronization

- [ ] Update both services' `docs/api.md` and deployment/operations documentation.
- [ ] Add the header to OpenAPI as optional input, document the new `400` response,
      and describe the stable error body/reason codes without making the header a hard
      client requirement when omission is intentionally supported.
- [ ] Update the shared Postman collection with a generated/static example value,
      never a secret.
- [ ] Document Cloud Logging queries using `jsonPayload.request_id` or the actual
      emitted structlog field shape.
- [ ] Add an adoption note for future `pf-svc-*` services.
- [ ] Verify any API gateway/proxy preserves the contract or does not overwrite
      `X-Request-ID`; if a browser frontend consumes the response, expose the header
      through CORS with `Access-Control-Expose-Headers`.

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
created by the service. Keep the `request_id` field in application log emission and
log queries until every active revision is confirmed either upgraded to the contract
or rolled back; do not remove the field from code or operational documentation during
the rollback window.

## 7. Completion evidence

The improvement is complete when both services emit and propagate the same validated
ID for a synthetic end-to-end request, the response exposes `X-Request-ID`, tests pass
for missing/invalid/retry/error paths, docs/Postman are synchronized, and no secrets or
sensitive payloads appear in evidence.
