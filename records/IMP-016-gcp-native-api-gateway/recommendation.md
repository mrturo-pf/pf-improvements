# Recommendation: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: implementation-in-progress
Level: L  
Scope: API Gateway, Cloud Run backend invocation, routing, cost, security, and observability.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)  
Approved: proposal preparation by `mrturo`  
Superseded-by: none

## 1. Executive recommendation

Adopt **Google Cloud API Gateway** as the preferred gateway technology and implement it
only after the pricing, IAM, OpenAPI, and connectivity gates in the plan pass. The live
route test invalidated the assumption that one prefixed gateway can preserve all
parameterized backend routes with `CONSTANT_ADDRESS`. The selected architecture is now
option B: one API Gateway plus one scale-to-zero Cloud Run proxy that strips the public
service prefix and forwards the original backend path.

API Gateway is the best fit for this ecosystem because it is managed, has no
user-managed always-on gateway compute, supports OpenAPI-based routing, can invoke
Cloud Run with a service account, and is operationally smaller than an additional
Cloud Run proxy or an external Application Load Balancer. Deploy it in `us-central1`,
which is supported and matches the backend region.

The rollout began as a **facade phase** using the generated `gateway.dev` hostname
and has now transitioned to enforcement. A custom domain remains deferred because the
documented path requires an external HTTP(S) Load Balancer integration with fixed
forwarding-rule cost and a Preview dependency.

In that phase:

- expose one gateway endpoint;
- route to both existing services;
- preserve backend API keys and `X-Request-ID`;
- keep the existing direct Cloud Run URLs available for rollback;
- measure real traffic and cost.

The separately approved enforcement phase has removed unauthenticated direct Cloud
Run access while preserving the application API-key contract.

## 2. Cost rationale

The gateway should be usage-based and scale independently of backend compute. Current
official evidence indicates 2 million Service Control calls per billing account are free
monthly, then usage pricing applies; Premium-tier egress can still cost money. Other
projects sharing the billing account consume the same free tier. Record the current
billing-account usage and actual first-month cost before expanding the design.

Alternatives rejected for the first phase:

- **Cloud Run proxy:** potentially cheap but adds another service, deployment, cold
  start, failure mode, and custom routing code.
- **External Application Load Balancer/serverless NEG:** useful for advanced edge
  control but adds a cost floor disproportionate to two low-volume services.
- **Apigee:** excessive cost and operational scope.
- **Cloud Endpoints/ESPv2:** overlapping proxy infrastructure without a demonstrated
  benefit over API Gateway.

## 3. Routing and security design

Use one API Gateway with explicit prefixed routes targeting a dedicated
`pf-gateway-proxy` Cloud Run service. The proxy strips `/reference` or `/income`,
forwards the original path/query/body to the selected backend, preserves
`X-Request-ID` and application headers, and returns the backend response unchanged.
The proxy must remain `min-instances=0`, run in `us-central1`, use service-to-service
identity tokens, and have bounded timeouts/retries. Each backend integration must use a
dedicated least-privilege service account with only the required `run.invoker`
permissions.

Do not put secret API-key values in the gateway configuration, OpenAPI document, Git,
or logs. During the facade phase, forward the existing `X-API-Key` header to retain
application behavior, but do not declare it as an API Gateway/Google consumer key;
otherwise the application key may be rejected by the gateway's own key validation.
A later authentication design may replace this, but that is not part of this improvement.

Preserve the common request-correlation contract:

- accept/forward `X-Request-ID`;
- allow the backend to generate it when omitted if the gateway does not generate one;
- return the effective ID;
- confirm the same ID in backend logs; verify gateway header retention separately and
  use Cloud Trace/request metadata if gateway logs omit arbitrary headers;
- never overwrite a valid ID with a new value at each hop.

## 4. Direct URL enforcement

Do not claim that a gateway protects the services merely because it exists. During the
facade phase, direct URLs remain a documented rollback path. For enforcement, choose
and validate one supported Cloud Run access model:

1. API Gateway authenticates to Cloud Run using its service account, the income
   runtime identity is granted invocation of reference, and Cloud Run removes public
   unauthenticated invocation; or
2. a different tested ingress/auth arrangement is approved with evidence.

Changing Cloud Run ingress or IAM is a production mutation and requires a Go/No-Go
record, health validation, rollback command, and evidence that API Gateway still reaches
both services.

## 5. Operational controls

- Verify whether gateway quotas work without Google consumer keys. If not, use Cloud
  Run max instances plus budget/volume alerts as the practical traffic guard; do not
  claim per-client quotas over the existing application `X-API-Key` header.
- Add alerts for gateway 4xx/5xx, backend 4xx/5xx, latency, and unexpected request
  volume.
- Keep Cloud Run scale-to-zero and existing max-instance protections.
- Record gateway config revision, backend revisions, service-account identity, and
  sanitized request IDs in rollout evidence.
- Verify `x-google-backend.deadline` behavior explicitly; do not assume the default is
  sufficient for Cloud Run cold starts and income-to-reference calls.
- Verify whether API Gateway logs retain arbitrary correlation headers. If not, use
  Cloud Trace/request metadata for the gateway-side join and backend `request_id` logs
  as authoritative evidence.
- Use the gateway's generated OpenAPI documentation only after comparing it with the
  service-owned API docs and Postman collection.

## 6. Go/No-Go recommendation

**Go** for the health/read-only proof of concept, which is already validated.

The route-preserving architecture decision is approved: implement one API Gateway plus
one `pf-gateway-proxy` Cloud Run service. Full route expansion remains gated on the
proxy contract, IAM, tests, cost validation, and rollback evidence.

**No-Go** for direct-URL lock-down until:

- the income runtime identity can invoke reference with a Google identity token in
  addition to the application API key;
- gateway routing is verified for both services;
- API-key and request-correlation behavior is verified;
- backend logs can be joined by `X-Request-ID`, and gateway-side correlation has been
  verified or documented through Cloud Trace/request metadata;
- rollback to direct URLs is tested;
- the owner accepts the measured recurring cost.
