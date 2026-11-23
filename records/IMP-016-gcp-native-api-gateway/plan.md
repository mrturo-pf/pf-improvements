# Plan: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: completed
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
- [x] Record the billing-account and Premium-tier egress review decision: no cost
      conclusion is claimed from the bounded POC; ongoing billing monitoring remains an
      operational responsibility outside this improvement.
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
- [x] Decide the first release is facade plus enforcement; the Go/No-Go was recorded
      after the reversible validation window.

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
- [x] Add gateway route examples and prefixes to service deployment documentation and
      Postman after the route-preserving proxy design was reviewed.

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
- [x] Close the bounded cost-observation gate with an explicit limitation: the POC
      evidence does not establish production request volume or gateway cost, so no cost
      conclusion is claimed.

## 4. Direct URL enforcement gate

- [x] Decide direct Cloud Run URLs must be inaccessible to public callers after the
      facade and identity-token gates pass.
- [x] Test the selected Cloud Run IAM model in a reversible window.
- [x] Grant the gateway identity least-privilege `run.invoker` access on each service.
- [x] Grant the `pf-svc-income` runtime identity `run.invoker` on `pf-svc-reference`
      and deploy Google identity-token propagation before removing public invocation.
- [x] Migrate the `pf-svc-income` backend client from direct reference URLs to the
      gateway facade; income revision `pf-svc-income-00019-m77` is deployed with the
      explicit gateway dependency URL and the direct runtime invoker was removed.
- [x] Remove public unauthenticated invocation after gateway routing and rollback passed;
      the application API-key contract remains unchanged.
- [x] Verify direct URL requests return `403` while gateway requests continue to return
      `200`.
- [x] Record a Go/No-Go decision and rollback command.

## 5. Tests and acceptance evidence

- [x] Validate live OpenAPI syntax and route inventory for both services; the active
      proxy-backed route map covers all 37 paths and 46 operations.
- [x] Add contract tests for proxy route mapping, headers, response statuses, and
      error behavior; local validation passed with 3 tests, Ruff, and bytecode checks.
      Identity-token integration remains covered by the deployed Cloud Run/Gateway path.
- [x] Validate gateway → proxy → income → reference request correlation and backend
      logs; the gateway does not retain arbitrary headers, so backend logs remain
      authoritative. The synthetic business request reached reference and returned a
      business-data `404`, not an IAM failure.
- [x] Preserve and validate rollback by retaining the prior health/read gateway config
      and the direct Cloud Run URLs; enforcement rollback is a documented IAM restore.
- [x] Close the traffic-control gate with the selected safe defaults documented: gateway
      quotas were not relied on without consumer-key attribution; Cloud Run max instances
      and budget/volume alerts remain operational controls rather than implementation
      blockers.
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
- the enforcement request returned business `404` only for missing future data, while
  income and reference logs shared the request ID and no IAM failure occurred;
- GitHub CI and deploy workflow passed for commit `21a534b` after WIF/deployer and
  build-service-account IAM were configured.

## 8. Facade and enforcement evidence

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
- direct unauthenticated Cloud Run invocation was removed after enforcement; direct
  requests returned `403` while gateway requests returned `200`;
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

## 9. Enforcement Go/No-Go

**Decision: GO — 2026-11-22.**

Enforcement was approved after validating the proxy, API Gateway, runtime IAM,
identity-token propagation, direct URL failure behavior, gateway responses, rollback
configuration, and backend log correlation. No application API-key contract was changed.

## 10. Closure

**Status: COMPLETED — 2026-11-22.**

The gateway facade, proxy, route map, IAM enforcement, service migration, observability,
acceptance validation, and rollback path are implemented and validated. The evidence does
not claim a production cost estimate or traffic-volume conclusion; those are explicitly
left to normal operational monitoring. No implementation blocker remains for IMP-016.
