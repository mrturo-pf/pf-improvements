# Investigation: gateway-owned API-key enforcement

Date: 2026-11-22  
Status: completed
Level: L  
Scope: GCP API Gateway, `pf-gateway-proxy`, `pf-svc-reference`, `pf-svc-income`, and client documentation.  
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: implementation authorized by `mrturo` on 2026-11-22  
Superseded-by: none

## 1. Problem statement

The current gateway rollout preserves the application `X-API-Key` contract through the
proxy and backend services. That leaves API-key policy in the services, which creates
an environment mismatch: local execution requires the same client credential as GCP,
and every service must know how to validate or manage the key. The desired boundary is
simpler: API Gateway owns the client credential policy; services receive only traffic
that has passed the gateway policy in GCP, while local direct development remains
credential-free.

This is a contract and security-boundary change, not merely a header rename.

## 2. Current known architecture

[IMP-016](../IMP-016-gcp-native-api-gateway/plan.md) established the following deployed path:

```text
API Gateway
  -> pf-gateway-proxy (Cloud Run, identity-token protected)
    -> pf-svc-reference / pf-svc-income (Cloud Run)
```

The gateway currently forwards application headers for compatibility. The backend
services retain application API-key behavior. The gateway's service-to-service identity
and Cloud Run IAM are separate from any client API key.

## 3. Design-gate findings (2026-11-23)

The first design gate is resolved from the deployed configuration and current official
Google Cloud documentation:

- API Gateway OpenAPI 2.0 API-key security uses `securityDefinitions` with `type: apiKey`,
  a configured `name`, and `in: header` or `in: query`, plus a `security` requirement.
- The selected placement is the standard `X-API-Key` header, validated by API Gateway.
  Backend services no longer inspect or require this header.
- API Gateway forwards original headers after validation; the official architecture
  documentation does not promise removal of a valid key. The proxy therefore removes
  `X-API-Key` before forwarding to either backend.
- `GET /health` operations remain outside the API-key security requirement so gateway and
  operational health checks do not need a consumer key. All business operations require
  the native gateway key.
- The original active config had no effective native API-key enforcement. The corrected
  active config applies operation/root security with health exemptions and the standard
  `X-API-Key` header.
- API keys identify and control the consumer project; they do not authenticate an end
  user. Cloud Run IAM and Google identity tokens remain the workload boundary.

Authoritative references:

- [Use API Keys](https://cloud.google.com/api-gateway/docs/authenticate-api-keys)
- [API Gateway architecture](https://cloud.google.com/api-gateway/docs/architecture-overview)
- [OpenAPI 2.0 extensions](https://cloud.google.com/api-gateway/docs/oasv2-extensions)

A restricted GCP API key resource is provisioned for the managed gateway service
`pf-backend-gateway-22kzlirwl1h1g.apigateway.coreassistant-474022.cloud.goog`.
The active resource is rotated outside this repository; raw key values are never stored
in Git, logs, or sanitized evidence.

Rotation is owned by the GCP project operator through the API Keys service. Developer
use will be through Postman Vault or an unsynced local current value only.
The IAM/ingress precondition was remediated on 2026-11-23 by removing the
`roles/run.invoker` binding for `allUsers` from `pf-svc-income`. The three services now
have only the expected service-account invokers. Validation returned `403` for direct
unauthenticated calls to both backend URLs and `200` for gateway health calls. Service
code, proxy sanitization, gateway enforcement, and Postman integration are deployed;
remaining work is acceptance evidence for service-to-service identity, logs, correlation,
and rollback.

## 4. Questions to resolve

- Which API Gateway OpenAPI security definition and extension should enforce the key?
- Should the gateway consume `X-API-Key` or the conventional `key` query/header
  placement, and can the chosen placement be kept out of backend business contracts?
- Does API Gateway strip the validated key before proxy forwarding, or must the proxy
  explicitly remove it? The final design must prevent backend code from depending on it.
- Which Google Cloud project owns the API consumer/key resources, and how are keys
  provisioned, rotated, disabled, and revoked without storing values in repositories?
- Which gateway response/status/body is returned for missing, invalid, and disabled keys?
  For this task, unauthorized means a valid key whose API restrictions do not include
  this API; that case must be tested separately.
- Does the gateway enforce the key on every public operation, including health, and is
  that compatible with readiness probes and operational monitoring?
- How do Postman and local clients select a gateway key without embedding one in the
  collection or environment committed to Git?
- How are backend-to-backend calls handled when income calls reference locally or
  through the gateway? They must not require a client API key merely because the public
  gateway does.

## 5. Security boundaries

- API Gateway API-key validation identifies and controls the public consumer contract;
  it does not authenticate an end user or replace Cloud Run IAM, identity tokens,
  application authorization, or data access controls.
- Cloud Run services must remain protected according to the approved ingress/IAM model.
- API-key values are secrets. Evidence may contain only names, fingerprints approved for
  sanitization, or result categories; never raw values.
- A backend must not silently accept a fake gateway marker header as proof of validation.
  Trust must come from the existing authenticated gateway-to-backend path, not from a
  client-controlled header.
- Local no-key behavior is intentional and must not weaken the GCP deployment policy.

## 6. Compatibility inventory

Affected contract surfaces include:

- API Gateway OpenAPI configuration and deployed API config;
- `pf-gateway-proxy` header forwarding and sanitization;
- `pf-svc-reference` and `pf-svc-income` middleware, settings, tests, and docs;
- income-to-reference HTTP client behavior in local and GCP modes;
- Postman collection and environments;
- service deployment documentation and generated API documentation;
- gateway, backend, and correlation-log evidence.

No database migration is expected.

## 7. Evidence required before implementation approval

- Official GCP documentation for API Gateway API-key authentication and quota behavior.
- A sanitized OpenAPI design showing the security definition and affected operations.
- A local test proving direct service calls do not require a key.
- A controlled GCP test proving valid and invalid gateway key outcomes.
- Evidence that backend logs and responses do not expose the key.
- A phased rollback design: before service key removal, restore the prior gateway, proxy,
  and service revisions together; after service key removal, roll back only gateway
  validation while services remain key-free and protected by Cloud Run IAM/ingress.
