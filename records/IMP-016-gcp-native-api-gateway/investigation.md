# Investigation: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: completed  
Level: L  
Scope: GCP ingress, API routing, authentication boundaries, request correlation, cost, and rollback for `pf-svc-reference` and `pf-svc-income`.  
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: proposal preparation by `mrturo`  
Superseded-by: none

## 1. Current state

The PF backend services are independently deployed Cloud Run services in
`coreassistant-474022` and `us-central1`:

- `pf-svc-reference` exposes a Cloud Run URL;
- `pf-svc-income` exposes a Cloud Run URL and calls `pf-svc-reference` directly;
- both services implement application-level `X-API-Key` authentication;
- both services now implement the ecosystem `X-Request-ID` contract;
- no API gateway, load balancer, API proxy, or shared public hostname is currently
  present in the repository architecture or service deployment documentation.

The current direct URLs are operationally simple and cheap, but every service is also
an independently visible public edge. A gateway could provide one documented entry
point, centralized routing, quotas, API documentation, and a controlled place for
future auth policy without adding an always-on VM or proxy container.

## 2. Candidate architectures

### A. Google Cloud API Gateway — preferred candidate

API Gateway is a managed GCP service configured from an OpenAPI document. It has no
user-managed idle compute and can route to Cloud Run backends using a gateway service
account. It is a natural fit for two low-traffic HTTP services and preserves the
scale-to-zero model.

Official evidence recorded below shows a usage-based API with no always-on gateway
instance, a 2-million-call monthly Service Control free tier per billing account, and
support for `us-central1`. It is expected to be near-zero for current low-volume traffic,
but Premium-tier egress and shared billing-account usage still require measurement.

### B. Cloud Run gateway service

A small FastAPI or proxy service could route requests to the two backends. It can
remain at `min-instances=0` and may fit Cloud Run's free tier, but it adds application
code, a new deployment, a new failure domain, and responsibility for routing/auth
behavior. It is cheaper only if API Gateway usage pricing exceeds the operational cost
of maintaining the proxy. It is not the preferred first option.

### C. External Application Load Balancer plus serverless NEGs

This is powerful and supports a stable hostname and more network controls, but it adds
load-balancer forwarding/processing and serverless NEG costs. For two low-volume
services it is unlikely to be the cheapest viable architecture.

### D. Apigee

Rejected for this scale and cost objective. Its enterprise API-management capabilities
are disproportionate to the PF ecosystem and introduce a much higher cost/operations
floor.

### E. Cloud Endpoints / ESPv2 on Cloud Run

Technically possible, but it still requires proxy deployment/operations and overlaps
with API Gateway. It has no demonstrated advantage for this use case.

## 3. Recommended boundary

Use one managed API Gateway in `us-central1`, the same region as the backends. The
facade phase must use the generated `gateway.dev` hostname, for example:

```text
https://GATEWAY_ID-HASH.REGION_CODE.gateway.dev/reference/...
https://GATEWAY_ID-HASH.REGION_CODE.gateway.dev/income/...
```

A custom domain is not part of the near-zero-cost phase: the documented custom-domain
path uses an external HTTP(S) Load Balancer integration that adds a fixed forwarding
rule cost, data-processing cost, and Preview dependency. Treat a custom domain as a
separate future improvement.

The OpenAPI gateway contract must map paths deterministically to existing backend
routes. Do not assume a multi-segment `{path}` wildcard preserves the backend path.
The route inventory must choose explicit route entries or a tested backend/path rewrite
strategy before deployment.

API Gateway pricing evidence confirms a monthly Service Control free tier of 2 million
calls per billing account, then usage-based pricing above that threshold. The current
PF traffic is expected to remain within the free call tier, subject to other projects
sharing the same billing account. Premium-tier egress still applies to data leaving
Google Cloud, so payload size and destination matter. Actual shared-account usage and
first-month egress remain implementation evidence, not yet measured.

The gateway must preserve:

- `X-Request-ID` exactly when valid;
- generated correlation behavior when the client omits it, or an explicitly documented
  gateway/backend ownership of generation;
- `X-API-Key` behavior during the compatibility phase;
- backend response status, body, and `X-Request-ID` headers.

The gateway should not log or expose API keys. Its service account should invoke Cloud
Run with least privilege. Existing application authentication remains authoritative
until a separate authentication migration is approved.

## 4. Direct URL and enforcement risk

Creating a gateway does not automatically prevent callers from bypassing the existing
Cloud Run URLs. The rollout must therefore distinguish:

1. **Facade phase:** gateway is introduced and validated while direct URLs remain as a
   rollback path.
2. **Enforcement phase:** direct unauthenticated invocation is removed only after the
   gateway path, service-account invocation, API-key behavior, correlation propagation,
   health checks, and rollback are proven.

The enforcement mechanism must be tested against Cloud Run ingress behavior. Do not
assume that changing ingress to `internal-and-cloud-load-balancing` is compatible with
API Gateway without a controlled validation; API Gateway's backend connectivity model
must be confirmed first.

If direct public invocation is removed from `pf-svc-reference`, the runtime identity of
`pf-svc-income` also needs `run.invoker` on the reference service, and the income client
must send a Google-signed identity token in addition to the application `X-API-Key`.
The gateway service account alone cannot preserve the existing internal call path.

## 5. Cost controls

- Prefer API Gateway over an always-on proxy.
- Keep both Cloud Run services at scale-to-zero.
- Do not add a Cloud SQL, VM, NAT, load balancer, or new always-on worker for routing.
- Verify whether API Gateway provides usable global quotas without Google consumer
  keys. If not, rely on Cloud Run max instances plus budget/volume alerts; do not
  describe per-client quotas as available over the application `X-API-Key` header.
- Use one gateway configuration and avoid duplicate gateways per service.
- Monitor API Gateway request count and Cloud Run invocations separately.
- Verify whether gateway logs retain arbitrary `X-Request-ID` headers. If they do not,
  use Cloud Trace/request metadata for the gateway-side join and treat backend
  `request_id` logs as the authoritative correlation evidence.
- Record the actual first-month gateway cost before considering a different architecture.

## 6. Current route inventory

The live OpenAPI documents were inspected on 2026-11-22:

- `pf-svc-reference`: 19 paths;
- `pf-svc-income`: 18 paths;
- the facade currently exposes four reviewed paths: two health routes and one
  read-only route per service.

The remaining 33 backend paths require an explicit route map before they are exposed
through the gateway. No multi-segment wildcard is assumed safe by default.

A live test showed that the single-gateway prefixed map cannot currently preserve
parameterized backend routes with `CONSTANT_ADDRESS`: `GET /income/payroll/556` reached
`pf-svc-income` as `/payroll/{period_id}` and returned `422`. API Gateway did not
substitute the path parameter in the backend address.

The viable options are:

1. change backends or add a proxy to strip prefixes (more application/operations cost);
2. use one API Gateway per service with the original backend paths and
   `APPEND_PATH_TO_ADDRESS` (still managed and near-zero, but two hostnames); or
3. keep the current four-route facade until a route-rewrite design is approved.

A single prefixed gateway must not be expanded to all routes without choosing one of
these options.

## 7. Quota conclusion

Official API Gateway documentation confirms custom metrics/quotas through
`x-google-management` and `x-google-quota`, using units such as `1/min/{project}`.
It does not confirm useful attribution of anonymous requests without Google consumer
keys to a consumer project. Therefore the POC does not claim per-client or custom
project quotas are available; Cloud Run max instances and budget/volume alerts remain
the fallback controls until tested.

## 8. Evidence required before implementation

- Current API route/OpenAPI inventory for both services;
- confirmed API Gateway pricing/free-tier/region data;
- confirmed route/deployment behavior and timeout/deadline documentation;
- gateway OpenAPI design with unchanged backend route mapping;
- service account and `run.invoker` least-privilege matrix;
- proof that `X-Request-ID` survives gateway → Cloud Run and backend-to-backend calls;
- facade and direct-URL rollback tests;
- explicit decision on whether/when direct Cloud Run URLs may be locked down.

## 9. Evidence sources

Consulted: 2026-11-22.

- [API Gateway pricing](https://cloud.google.com/api-gateway/pricing)
- [API Gateway deployment model](https://docs.cloud.google.com/api-gateway/docs/deployment-model)
- [API Gateway quotas](https://docs.cloud.google.com/api-gateway/docs/quotas)
- [OpenAPI quota extensions](https://docs.cloud.google.com/api-gateway/docs/oasv2-extensions#x-google-management)
- [API Gateway with load balancing](https://docs.cloud.google.com/api-gateway/docs/gateway-load-balancing)
