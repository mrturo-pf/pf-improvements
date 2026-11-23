# Recommendation: gateway-owned API-key enforcement

Date: 2026-11-22  
Status: approved  
Level: L  
Scope: API Gateway authentication policy, proxy boundary, backend services, local development, and client tooling.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)  
Approved: implementation authorized by `mrturo` on 2026-11-22  
Superseded-by: none

## 1. Executive recommendation

Adopt API Gateway as the sole owner of the external API-key policy for GCP traffic.
Remove API-key validation and management from `pf-svc-reference` and
`pf-svc-income`, and keep local direct service execution free of API-key requirements.
The gateway should validate the key using its native API-key mechanism before routing
the request to `pf-gateway-proxy`.

The proxy must not reimplement API-key validation and must not forward the client key to
backend services. The target contract is that the service APIs do not know that a client
key exists. If implementation evidence shows a temporary compatibility exception is
unavoidable, it requires a separately approved change with a named owner, expiry date,
removal issue, and explicit proof that no backend validation is reintroduced.

## 2. Why this boundary

- One public enforcement point avoids duplicated middleware and divergent key rules.
- Local development remains simple and deterministic: direct service calls need no
  gateway-only credential.
- Backend services remain reusable behind other trusted callers and in tests.
- Key rotation, disablement, consumer ownership, and gateway rejection stay in the
  infrastructure boundary where they belong.
- Cloud Run IAM and identity tokens continue to protect service-to-service invocation;
  an API key is not a replacement for that control.

## 3. Proposed contract

```text
Local:
  client -> http://localhost:<service> -> backend
  API key: not required and not inspected

GCP:
  client -> API Gateway + valid API key -> pf-gateway-proxy -> backend
  API key: identified and controlled by API Gateway; not required by backend code

GCP direct-to-Cloud Run request:
  rejected by Cloud Run IAM/ingress

GCP invalid request:
  API Gateway rejects before proxy/backend business handling
```

The exact header/query placement and gateway response schema must be selected during the
plan's design gate from current GCP documentation. Do not assume that the existing
`X-API-Key` application header is automatically a native API Gateway key contract.

## 4. Required implementation principles

1. **Single responsibility:** gateway policy validates public keys; services implement
   domain behavior, not gateway credential management.
2. **No silent fallback:** a GCP request must not bypass gateway validation through a
   client-controlled header or backend compatibility flag.
3. **Environment clarity:** local no-key access must be documented and tested; it must
   not be confused with public GCP access.
4. **Secret hygiene:** keys are provisioned outside Git and injected only into local
   developer tooling through an approved secret mechanism when needed.
5. **Preserve unrelated contracts:** request correlation, response semantics, Cloud Run
   IAM, identity-token propagation, and business authorization remain explicit.
6. **Reversible rollout:** before service key removal, rollback restores the prior
   gateway, proxy, and service revisions together because their contracts are coupled.
   After service key removal, rollback is gateway-only: disable gateway key validation
   while services remain key-free and protected by Cloud Run IAM/ingress. The earlier
   rollback temporarily restores the previous state; the target state never includes
   service-owned key validation.

## 5. Alternatives rejected

- **Keep validation in every service:** duplicates policy, forces local credentials, and
  violates the requested ownership boundary.
- **Validate in both gateway and services:** creates two authorities and makes local/GCP
  behavior unnecessarily coupled.
- **Use a secret header added by the proxy:** a marker is not proof of gateway validation
  and would create a fragile, spoofable internal contract.
- **Use Cloud Run IAM as the client API-key mechanism:** IAM protects workload identity,
  not the intended public consumer-key lifecycle.

## 6. Go/No-Go recommendation

**Go** to close the design gates and prepare implementation.

Implementation and deployment require separate approval. Do not deploy until the plan
confirms native API Gateway key behavior, key lifecycle ownership, health/readiness
implications, local and GCP test paths, proxy sanitization, and rollback. A valid key
must never be included in repository artifacts or test output.
