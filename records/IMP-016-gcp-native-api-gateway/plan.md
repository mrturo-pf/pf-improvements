# Plan: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: implementation-in-progress
Level: L  
Scope: GCP API Gateway, Cloud Run services, IAM, routing, observability, Postman, and cost evidence.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: 2026-11-22 by `mrturo`; facade proof of concept implementation started
Superseded-by: none

## 1. Gates before implementation

- [x] Confirm the facade hostname is the generated `gateway.dev` hostname; custom
      domains are deferred because the documented Load Balancer integration has a fixed
      cost and Preview status.
- [x] Confirm current official evidence: `us-central1` is supported and 2 million
      Service Control calls per billing account are free monthly.
- [ ] Record shared billing-account usage and expected Premium-tier egress cost before
      provisioning.
- [x] Inventory both live OpenAPI documents: reference has 19 paths and income has 18
      paths. A full explicit map was generated as 37 paths and 46 operations, but the
      live parameterized-route test showed that one prefixed gateway cannot preserve
      those paths with `CONSTANT_ADDRESS`.
- [x] Select option B: one API Gateway plus a dedicated `pf-gateway-proxy` Cloud Run
      service that strips `/reference` and `/income` prefixes and forwards original
      backend paths. Do not expand the single prefixed gateway directly.
- [x] Confirm the facade gateway-to-Cloud-Run authentication model and service-account
      permissions; enforcement IAM/token design remains separate. No secrets are in the
      gateway config.
- [x] Confirm `X-Request-ID` is preserved through proxy/backend logs; gateway request
      logs omit the arbitrary header, so backend logs are authoritative and Cloud Trace
      remains the gateway-side fallback.
- [ ] Decide whether the first release is facade-only (recommended) or includes direct
      Cloud Run enforcement; enforcement requires a separate Go/No-Go.

## 2. Design and configuration

- [x] Create the final sanitized OpenAPI document targeting `pf-gateway-proxy`; the
      active config contains 37 paths and 46 operations with explicit header parameters.
- [x] Create the independent `pf-gateway-proxy` service repository and implement the
      prefix stripping, forwarding, identity-token, timeout, retry, and correlation
      contract; Cloud Run build and deployment validation passed.
- [x] Define gateway API/config/gateway resource names and region using stable naming.
- [x] Define and provision the dedicated gateway service account with least-privilege
      `run.invoker` on both Cloud Run services for the facade; enforcement still needs
      the income runtime invocation/token design.
- [ ] Verify whether quotas work without Google consumer keys. Official docs confirm
      custom quotas use `x-google-quota` and `1/min/{project}`, but do not confirm useful
      attribution for anonymous requests; if unavailable, define Cloud Run max instances
      and budget/volume alerts as the practical traffic controls.
- [x] Define request limits, timeout behavior, and 4xx/5xx mappings; confirm the
      OpenAPI 2.0 `x-google-backend.deadline` behavior and set the POC to 30 seconds.
- [x] Define and validate that API Gateway forwards `X-API-Key` unchanged without
      configuring it as a Google API consumer key during the facade phase.
- [x] Define rollback to the existing direct Cloud Run URLs; the prior health/read config
      remains available for gateway rollback.
- [ ] Add gateway route examples to API documentation and Postman only after the
      route-preserving expansion design is reviewed.

## 3. Read-only / facade proof of concept

- [x] Provision the health-only API Gateway facade without changing direct Cloud Run
      traffic or public invocation.
- [x] Route `GET /health` for both services first.
- [x] Validate gateway responses, backend revisions, and status codes.
- [x] Validate authenticated/read-only backend requests without logging API-key values.
- [x] Validate supplied, omitted, and malformed `X-Request-ID` through the gateway;
      backend responses/logs preserve generated or supplied IDs.
- [x] Query backend logs with the same sanitized request ID; gateway request logs do not
      retain the arbitrary header, so the backend log is authoritative for this POC.
- [ ] Record actual request count and observed gateway cost after a bounded observation
      window; no cost conclusion is made from the first health calls.

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

- [x] Validate live OpenAPI syntax and route inventory for both services; the active
      proxy-backed route map covers all 37 paths and 46 operations.
- [x] Add contract tests for proxy route mapping, headers, response statuses, and
      error behavior; local validation passed with 3 tests, Ruff, and bytecode checks.
      Identity-token integration remains covered by the deployed Cloud Run/Gateway path.
- [x] Validate gateway → proxy → income route correlation and backend logs; the
      gateway does not retain arbitrary headers, so backend logs remain authoritative.
      A full income → reference business flow remains a future evidence case.
- [x] Preserve and validate rollback by retaining the prior health/read gateway config
      and the unchanged direct Cloud Run URLs; enforcement rollback remains pending.
- [ ] Test the selected traffic control with bounded synthetic traffic: gateway quotas
      if usable without consumer keys, otherwise Cloud Run max instances plus budget/
      volume alert behavior.
- [x] Verify no credentials, personal data, payroll data, or raw production payloads are
      present in configs, logs, or evidence.

## 6. Rollout and rollback

1. Review cost/IAM/OpenAPI gates.
2. Implement and deploy `pf-gateway-proxy` with `min-instances=0` and direct URLs
   unchanged.
3. Point the facade gateway at the proxy and validate health, auth compatibility,
   correlation, logs, and cost.
4. Observe a bounded window and decide whether enforcement is worthwhile.
5. If approved, enforce gateway invocation in a separate change and maintenance window.
6. Roll back by restoring the prior Cloud Run IAM/ingress settings and directing clients
   to the existing service URLs.

No database migration or application-domain change is expected.

## 7. Proxy implementation evidence

Provisioned 2026-11-22 in `coreassistant-474022`:

- service: `pf-gateway-proxy`;
- revision: `pf-gateway-proxy-00004-kdx`;
- runtime service account: `pf-gateway-proxy@coreassistant-474022.iam.gserviceaccount.com`;
- backend invocation permissions granted on both PF services;
- gateway invocation permission granted on the proxy;
- proxy configured with `min-instances=0`, max two instances, 512 MiB, one CPU, and
  30-second timeout;
- full proxy-backed API config `full-proxy-headers-20261122` is active;
- parameterized route `/income/payroll/556` returned `200` through the gateway;
- proxy and income backend logs shared the same `X-Request-ID` for that request;
- response headers no longer duplicate `X-Request-ID` after proxy normalization;
- GitHub CI and deploy workflow passed for commit `21a534b` after WIF/deployer and
  build-service-account IAM were configured.

## 8. Facade proof-of-concept evidence

Validated 2026-11-22 in `coreassistant-474022`:

- Gateway: `pf-backend-gateway-poc`;
- Full OpenAPI map: `pf-gateway-proxy.json`, containing 37 paths and 46 operations;
- hostname: `pf-backend-gateway-poc-88uq0qjn.uc.gateway.dev`;
- state reached `ACTIVE`;
- `GET /reference/health` returned `200` and preserved the supplied `X-Request-ID`;
- `GET /income/health` returned `200` and preserved the supplied `X-Request-ID`;
- backend logs for both services contained matching request start/completion events;
- API Gateway request logs recorded method/URL/status metadata but did not expose the
  arbitrary `X-Request-ID` header in the inspected entries;
- direct Cloud Run URLs and public invocation were not changed;
- the initial prefixed `CONSTANT_ADDRESS` map was rejected after `/income/payroll/556`
  returned `422`; the proxy-backed `APPEND_PATH_TO_ADDRESS` map corrected this;
- authenticated facade routes returned `200` for both services and preserved application
  API-key behavior;
- the final API config uses an explicit 30-second `x-google-backend.deadline` and
  reached `ACTIVE` through the gateway update;
- omitted correlation IDs generated valid response IDs, and malformed IDs returned
  `400` with a generated error-context ID;
- gateway request logs recorded successful method/URL/status metadata, while backend
  logs contained the detailed correlation events.
