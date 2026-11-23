# Brief: gateway-owned API-key enforcement

Date: 2026-11-22  
Status: approved  
Level: L  
Scope: API Gateway API-key validation, `pf-gateway-proxy`, `pf-svc-*` local/runtime behavior, documentation, and client contracts.  
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)  
Approved: implementation authorized by `mrturo` on 2026-11-22  
Superseded-by: none

## Objective

Move API-key management to the GCP gateway boundary. `pf-svc-reference` and
`pf-svc-income` must not validate, require, generate, store, or otherwise manage
client API keys. Requests reaching a service directly in local development must work
without an API key. Requests entering through the GCP API Gateway must be accepted
only when the gateway has validated the required key.

The gateway is the single public policy enforcement point:

```text
local client -> pf-svc-* directly -> no API key required
GCP client   -> API Gateway -> pf-gateway-proxy -> pf-svc-* -> gateway-validated request
GCP client   -> pf-svc-* directly -> rejected by Cloud Run IAM/ingress
```

## Security precondition

Before removing service-owned API-key validation, verify that `pf-svc-reference`,
`pf-svc-income`, and `pf-gateway-proxy` are invocable only by the identities authorized
by the approved Cloud Run IAM and ingress policy. A client API key is not the control
that protects direct GCP Cloud Run URLs.

## Required behavior

- API Gateway owns the external API-key requirement and rejection response.
- Backend services do not contain API-key validation or key-management logic.
- Local service execution and local service-to-service calls do not require an API key.
- GCP gateway traffic is rejected before backend business logic when the gateway key is
  missing, invalid, disabled, or unauthorized for the configured API. Unauthorized means
  a valid key whose API restrictions do not include this API.
- API-key values are never committed, logged, returned, or copied into backend config.
- The gateway-to-backend identity-token contract remains separate from client API keys.
- `X-Request-ID`, response contracts, and backend authorization unrelated to API keys are
  preserved.
- Postman and service documentation clearly distinguish local direct access from GCP
  gateway access.

## Non-objectives

- Replacing Cloud Run IAM or gateway-to-proxy identity tokens.
- Adding API-key checks to the proxy or any `pf-svc-*` application.
- Defining a new database table or persistence model for keys.
- Treating `X-API-Key` as a substitute for Google identity tokens.
- Removing unrelated business authorization or sensitive-data controls.

## Acceptance criteria

1. A reviewed gateway configuration validates API keys at API Gateway and documents the
   selected key location, consumer project, API/config association, and failure behavior.
2. Local direct calls to each `pf-svc-*` service succeed without an API key.
3. GCP gateway calls succeed with a valid key and fail at the gateway with a documented
   response when the key is missing, invalid, disabled, or unauthorized.
4. Backend services and the proxy do not validate or manage client API keys.
5. No API-key value appears in source, deployment configuration, logs, fixtures, or
   sanitized evidence.
6. Postman environments and service API documentation show the correct local and GCP
   flows without embedding secrets.
7. Rollback and compatibility behavior are tested, including request correlation and
   backend-to-backend calls.
8. The direct Cloud Run exposure policy remains unchanged unless separately approved;
   the precondition is verified before implementation: only authorized identities can
   invoke the services and proxy. Gateway API-key validation is not presented as Cloud
   Run network or IAM protection.
