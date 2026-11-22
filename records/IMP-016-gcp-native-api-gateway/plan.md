# Plan: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: proposed  
Level: L  
Scope: GCP API Gateway, Cloud Run services, IAM, routing, observability, Postman, and cost evidence.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: proposal preparation only by `mrturo`; implementation requires a follow-up authorization  
Superseded-by: none

## 1. Gates before implementation

- [x] Confirm the facade hostname is the generated `gateway.dev` hostname; custom
      domains are deferred because the documented Load Balancer integration has a fixed
      cost and Preview status.
- [x] Confirm current official evidence: `us-central1` is supported and 2 million
      Service Control calls per billing account are free monthly.
- [ ] Record shared billing-account usage and expected Premium-tier egress cost before
      provisioning.
- [ ] Inventory both services' live routes/OpenAPI and define an explicit gateway route
      map without changing backend route semantics; do not rely on an untested
      multi-segment wildcard.
- [ ] Confirm the gateway-to-Cloud-Run authentication model and required service-account
      permissions; no secret values in the gateway config.
- [ ] Confirm how `X-Request-ID` is preserved/generated at the gateway boundary and
      appears in gateway/backend logs; use Cloud Trace as a fallback if gateway logs
      do not retain arbitrary headers.
- [ ] Decide whether the first release is facade-only (recommended) or includes direct
      Cloud Run enforcement; enforcement requires a separate Go/No-Go.

## 2. Design and configuration

- [ ] Create a sanitized gateway OpenAPI document with explicit backend integrations
      for `pf-svc-reference` and `pf-svc-income`.
- [ ] Define gateway API/config/gateway resource names and region using stable naming.
- [ ] Define the dedicated gateway service account and least-privilege `run.invoker`
      bindings for both Cloud Run services; for enforcement, define income runtime
      invocation of reference and Google identity-token propagation.
- [ ] Verify whether quotas work without Google consumer keys; if not, define Cloud Run
      max instances and budget/volume alerts as the practical traffic controls.
- [ ] Define request limits, timeout behavior, and 4xx/5xx mappings; confirm
      `x-google-backend.deadline` explicitly.
- [ ] Define that API Gateway forwards `X-API-Key` unchanged without configuring it as
      a Google API consumer key during the facade phase.
- [ ] Define rollback to the existing direct Cloud Run URLs.
- [ ] Add gateway route examples to API documentation and Postman only after the
      OpenAPI route map is reviewed.

## 3. Read-only / facade proof of concept

- [ ] Provision the cheapest viable API Gateway resources in a non-destructive manner.
- [ ] Route `GET /health` for both services first.
- [ ] Validate gateway responses, backend revision names, latency, and status codes.
- [ ] Validate an authenticated/read-only backend request without logging API-key values.
- [ ] Validate `X-Request-ID` supplied, omitted, and malformed behavior through the gateway.
- [ ] Query backend logs with the same sanitized request ID; verify gateway header
      retention and use Cloud Trace/request metadata if gateway logs omit it.
- [ ] Record actual request count and observed gateway cost.

## 4. Direct URL enforcement gate

- [ ] Decide whether direct Cloud Run URLs must be inaccessible to public callers.
- [ ] If yes, test the selected Cloud Run IAM/ingress model in a reversible window.
- [ ] Grant the gateway identity least-privilege `run.invoker` access on each service.
- [ ] Grant the `pf-svc-income` runtime identity `run.invoker` on `pf-svc-reference`
      and implement Google identity-token propagation before removing public invocation.
- [ ] Remove public unauthenticated invocation only after gateway routing and rollback
      pass; do not remove the application API-key contract in the same step.
- [ ] Verify direct URL requests fail as intended while gateway requests continue to pass.
- [ ] Record a Go/No-Go decision and rollback command.

## 5. Tests and acceptance evidence

- [ ] Validate OpenAPI syntax and route coverage for both services.
- [ ] Add contract tests for route mapping, headers, response statuses, and error behavior.
- [ ] Add end-to-end tests for request correlation through gateway → income → reference;
      accept backend-log correlation even if gateway logs omit arbitrary headers, with
      Cloud Trace/request metadata as the documented fallback.
- [ ] Test direct URL rollback before any enforcement mutation.
- [ ] Test the selected traffic control with bounded synthetic traffic: gateway quotas
      if usable without consumer keys, otherwise Cloud Run max instances plus budget/
      volume alert behavior.
- [ ] Verify no credentials, personal data, payroll data, or raw production payloads are
      present in configs, logs, or evidence.

## 6. Rollout and rollback

1. Review cost/IAM/OpenAPI gates.
2. Deploy facade gateway with direct URLs unchanged.
3. Validate health, auth compatibility, correlation, logs, and cost.
4. Observe a bounded window and decide whether enforcement is worthwhile.
5. If approved, enforce gateway invocation in a separate change and maintenance window.
6. Roll back by restoring the prior Cloud Run IAM/ingress settings and directing clients
   to the existing service URLs.

No database migration or application-domain change is expected.
