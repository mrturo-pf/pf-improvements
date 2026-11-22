# Brief: GCP-native API gateway for `pf-svc-*`

Date: 2026-11-22  
Status: observation  
Level: L  
Scope: Managed GCP gateway, Cloud Run backend routing, auth compatibility, request correlation, and cost.  
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: proposal preparation by `mrturo`  
Superseded-by: none

## Objective

Evaluate and, if approved by the implementation gates, introduce a single GCP-native
entry point for the PF backend services while preserving scale-to-zero and keeping
incremental cost at zero or as close to zero as the actual GCP pricing permits.

The preferred candidate is Google Cloud API Gateway routing to:

```text
pf-svc-reference
pf-svc-income
```

## Required behavior

- Generated `gateway.dev` hostname in the near-zero-cost phase and documented service
  path prefixes; custom domains are explicitly out of scope for this phase;
- deterministic routing to existing backend paths;
- preservation of `X-Request-ID` and `X-API-Key` during compatibility rollout;
- gateway-to-Cloud-Run authentication through a least-privilege service account;
- unchanged backend response bodies/statuses in the first phase;
- documented traffic controls (gateway quotas if usable without consumer keys; otherwise
  Cloud Run max instances plus budget/volume alerts) that prevent accidental traffic
  amplification;
- backend logs joined by `X-Request-ID`, with gateway header retention verified and
  Cloud Trace/request metadata available as the gateway-side fallback;
- rollback to the existing direct service URLs.

## Cost objective

Use a managed, usage-based gateway with no always-on user-managed compute. Current
official pricing evidence indicates 2 million Service Control calls per billing account
are free each month, with usage charges above that threshold and possible Premium-tier
egress. The implementation must document shared billing-account usage and expected
monthly cost at current traffic.

No new VM, NAT gateway, load balancer, Cloud SQL instance, or always-on proxy is in
scope for the preferred design.

## Non-objectives

- Replacing application-level API-key authentication in the first phase;
- redesigning backend routes or request/response bodies;
- introducing Apigee or enterprise API-management features;
- locking down direct Cloud Run URLs before a separate enforcement gate passes;
- changing the `X-Request-ID` contract;
- adding a database, queue, or permanent proxy service solely for routing.

## Acceptance criteria

1. A reviewed OpenAPI gateway configuration routes both backend services without route
   ambiguity or accidental public backend exposure; route mapping does not depend on an
   untested multi-segment wildcard.
2. API Gateway pricing, free tier, quota, and region availability are recorded from
   current authoritative GCP documentation.
3. Gateway requests reach the intended Cloud Run revision and preserve response status,
   body, and `X-Request-ID`.
4. The gateway service account has only the required Cloud Run invocation permissions;
   any enforcement phase also grants income runtime invocation of reference and provides
   an identity-token design.
5. Existing application API-key behavior remains compatible; the gateway does not treat
   `X-API-Key` as a Google API consumer key during the facade phase.
6. A synthetic request can be joined across backend logs by `X-Request-ID`; gateway log
   header retention is separately verified, with Cloud Trace as fallback evidence.
7. Direct URL rollback is tested and documented.
8. No direct-URL enforcement occurs without an explicit Go/No-Go decision.
9. Actual gateway and Cloud Run costs are measured after rollout.
