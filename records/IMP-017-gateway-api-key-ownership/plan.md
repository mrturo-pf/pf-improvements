# Plan: gateway-owned API-key enforcement

Date: 2026-11-22  
Status: approved  
Level: L  
Scope: API Gateway key policy, proxy sanitization, backend services, local development, GCP rollout, and client documentation.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: implementation authorized by `mrturo` on 2026-11-22  
Superseded-by: none

## 1. Design gates before implementation

- [ ] Confirm authoritative GCP API Gateway API-key behavior, supported OpenAPI
      configuration, key placement, consumer-project association, and rejection codes.
      The unauthorized test case means a valid key whose API restrictions do not include
      this API.
- [ ] Decide whether public health endpoints require a key or use a separately approved
      operational path; do not break Cloud Run/Gateway health validation accidentally.
- [ ] Define the key lifecycle owner, provisioning path, rotation, disablement, revocation,
      and access audit. No raw key may enter Git, CI logs, or sanitized evidence.
- [ ] Confirm whether API Gateway strips the validated key before proxy forwarding. If it
      does not, define proxy sanitization and prove backend logs never record the value.
- [ ] Verify the precondition from [IMP-016](../IMP-016-gcp-native-api-gateway/plan.md):
      `pf-svc-reference`, `pf-svc-income`, and `pf-gateway-proxy` are invocable only by
      authorized identities under Cloud Run IAM/ingress. Define the distinction between
      gateway API keys and Cloud Run identity tokens; preserve least privilege.
- [ ] Define local configuration so direct service execution requires no API key and no
      gateway-only setting is silently treated as a backend credential.

## 2. Service and proxy changes

- [ ] If API Gateway does not remove the native key before forwarding, deploy native-key
      sanitization in `pf-gateway-proxy` before activating gateway validation (§6 step 2).
- [ ] Then deploy `pf-svc-reference` and `pf-svc-income` changes: disable API-key
      enforcement while retaining the old configuration and code temporarily for the
      pre-step-5 rollback path.
- [ ] Update income-to-reference calls so local direct calls work without a client key;
      GCP identity-token behavior remains explicit and separate. In GCP, the call goes
      directly from income to reference and does not traverse the public gateway.
- [ ] After both services accept key-free requests, update `pf-gateway-proxy` to remove
      client API-key values before forwarding to services. No compatibility exception is
      part of this plan; any unavoidable exception requires a separate approval, named
      owner, expiry date, removal issue, and evidence that backend validation is not
      reintroduced.
- [ ] After the gateway and proxy transition is proven, remove API-key validation code,
      generation, storage, and required settings from both services; this is the
      irreversible service-owned-key removal in step 5.
- [ ] Add tests proving services do not require or inspect client API keys and that
      unrelated authorization remains intact.
- [ ] Keep all monetary and domain behavior unchanged; no database migration is expected.

## 3. Gateway configuration

- [ ] Add native API Gateway API-key security to the sanitized OpenAPI configuration for
      the approved public operations.
- [ ] Configure the GCP API/config/gateway resources without committing key values.
- [ ] Validate missing, invalid, disabled, and unauthorized keys at the gateway boundary;
      unauthorized is a valid key whose API restrictions exclude this API.
- [ ] Validate valid-key routing through proxy to both services and preserve status,
      body, `X-Request-ID`, and approved response headers.
- [ ] Confirm backend business requests cannot bypass gateway validation through a fake
      client-controlled marker header.

## 4. Local and GCP acceptance tests

- [ ] Local `pf-svc-reference` direct request succeeds without an API key.
- [ ] Local `pf-svc-income` direct request succeeds without an API key.
- [ ] Local income-to-reference request succeeds without a client API key.
- [ ] GCP income-to-reference request succeeds directly with the income runtime identity
      token, without a client API key and without traversing the public gateway.
- [ ] GCP request with a valid gateway key succeeds for approved reference routes.
- [ ] GCP request with a valid gateway key succeeds for approved income routes.
- [ ] GCP requests with missing, invalid, disabled, or unauthorized keys are rejected by
      API Gateway before backend business handling.
- [ ] Verify backend logs, proxy logs, traces, and response bodies contain no raw key.
- [ ] Verify correlation separately for gateway rejections and successful backend
      requests: a client-supplied valid `X-Request-ID` is expected to be preserved in a
      gateway rejection if API Gateway exposes it; no backend-generated ID is expected
      because rejected requests do not reach the proxy. Successful requests retain the
      existing end-to-end correlation contract.
- [ ] Verify direct Cloud Run/IAM behavior remains governed by the
      [IMP-016](../IMP-016-gcp-native-api-gateway/plan.md) policy and is not weakened by
      removing application API-key checks.
- [ ] Exercise rollback before step 5: restore gateway, proxy, and service revisions
      together, then verify a client sends the prior application key and the request
      succeeds.
- [ ] Exercise rollback after step 5: disable gateway key validation only, keep services
      key-free, and verify requests remain protected by IAM/ingress without restoring
      service-owned API-key validation.

## 5. Documentation and client compatibility

- [ ] Update service API documentation to state that local direct calls need no key and
      GCP public calls require the gateway key.
- [ ] Update gateway documentation with key provisioning and rotation references without
      exposing secrets.
- [ ] Update Postman collection and environments to separate local no-key requests from
      GCP requests that read a developer-provided secret from Postman Vault or a local
      current value that is never synced. The initial value must remain empty and no key
      may be committed.
- [ ] Add migration notes for clients currently sending `X-API-Key`; document whether
      the native gateway key uses that header or a different placement.
- [ ] Update deployment and rollback runbooks.

## 6. Rollout and rollback

1. Validate design gates, especially Cloud Run IAM/ingress, and create sanitized gateway
   configuration.
2. Deploy gateway validation in a reversible configuration and test rejection behavior.
   During this step the client sends the native gateway key and, because services still
   enforce the old contract, the existing application key as well when the two mechanisms
   use distinct placements. If both mechanisms use the same header, do not proceed until
   the design gate defines a non-conflicting transition; two different values cannot
   share one header. If the design gate confirms that API Gateway does not remove the
   native key before forwarding, deploy proxy sanitization for the native key before
   activating gateway validation; there must be no exposure window in proxy or backend
   logs.
3. Deploy service changes first. Disable service key enforcement through an explicit
   deployment configuration, never through a request-controlled flag; retain the old
   configuration and code for rollback. Verify local no-key and GCP service-to-service
   behavior. Then deploy proxy sanitization so it removes the client key before backend
   forwarding.
4. Validate local no-key and GCP valid/invalid-key flows. Public GCP clients now send
   only the native gateway key; backend-to-backend calls use identity tokens and no
   client key.
5. After the gateway and proxy transition passes, remove service-owned API-key settings,
   secrets, validation code, and compatibility code. This is the point of no return for
   the pre-step-5 rollback path.

Rollback is phase-specific:

- **Before step 5:** restore the prior gateway configuration, prior proxy revision, and
  prior service revision together. The backend key configuration still exists in this
  phase, and restoring only the service would leave the sanitized proxy unable to satisfy
  the old backend contract.
- **After step 5:** roll back only the gateway validation configuration. Services remain
  key-free; Cloud Run IAM/ingress and service-to-service identity tokens remain the
  protection boundary. The post-step-5 rollback must not restore a revision that
  reintroduces service-owned API-key validation.

No production key value is to be copied into an issue, plan, repository, command output,
or test artifact.

## 7. Acceptance traceability

| Brief criterion | Plan coverage |
|---|---|
| 1. Reviewed gateway configuration | §1 design gates; §3 gateway configuration |
| 2. Local no-key calls | §2 service changes; §4 local tests |
| 3. Valid/invalid GCP gateway behavior | §3 gateway configuration; §4 GCP tests |
| 4. No service/proxy key management | §2 service and proxy changes |
| 5. No key leakage | §1 lifecycle; §4 log/evidence test |
| 6. Postman and documentation | §5 documentation and client compatibility |
| 7. Rollback and compatibility | §4 rollback and service-to-service tests; §6 phase-specific rollback |
| 8. IAM/ingress precondition | §1 IAM gate; §4 direct Cloud Run test |

## 8. Decision record

**Decision: GO — implementation authorized by `mrturo` on 2026-11-22.**

The approved final state is gateway-owned API-key enforcement for GCP and no API-key
requirement in local direct service execution. Implementation must follow the design
gates, phased rollout, acceptance tests, and rollback procedures defined above.
