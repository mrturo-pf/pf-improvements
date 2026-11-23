# Plan: gateway-owned API-key enforcement

Date: 2026-11-22  
Status: approved  
Level: L  
Scope: API Gateway key policy, proxy sanitization, backend services, local development, GCP rollout, and client documentation.  
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)  
Approved: implementation authorized by `mrturo` on 2026-11-22  
Superseded-by: none

## 1. Design gates before implementation

- [x] Confirm authoritative GCP API Gateway API-key behavior, supported OpenAPI
      configuration, key placement, consumer-project association, and rejection codes.
      The unauthorized test case means a valid key whose API restrictions do not include
      this API. Evidence: official GCP API Gateway documentation; selected placement is
      the standard `X-API-Key` header.
- [x] Keep `GET /health` operations outside the gateway API-key requirement so health and
      operational checks remain keyless; require the key for business operations.
- [x] Define the key lifecycle owner, provisioning path, rotation, disablement, revocation,
      and access audit. The GCP project operator owns the restricted API Key resource;
      developer values use Postman Vault or an unsynced local current value. No raw key
      may enter Git, CI logs, or sanitized evidence. Provisioned resource ID:
      `e1a20932-0c9f-4fd9-a236-ef233e765d88`.
- [x] Confirm API Gateway does not promise to strip validated original headers. Define
      proxy sanitization for the gateway-owned standard `X-API-Key` and require it before
      gateway validation activation; backend logs must never record the value.
- [x] Verify the precondition from [IMP-016](../IMP-016-gcp-native-api-gateway/plan.md):
      `pf-svc-reference`, `pf-svc-income`, and `pf-gateway-proxy` are now invocable only
      by authorized identities under Cloud Run IAM/ingress. On 2026-11-23, removed the
      `allUsers` `roles/run.invoker` binding from `pf-svc-income`; direct unauthenticated
      calls to both backend URLs returned `403`, while gateway health calls returned
      `200`. API keys identify/control the consumer project while identity tokens and
      IAM protect workload invocation.
- [x] Define local configuration so direct service execution requires no API key and no
      gateway-only setting is silently treated as a backend credential. Both services now
      run without client API-key settings.

## 2. Service and proxy changes

- [x] Deploy native-key sanitization in `pf-gateway-proxy` before activating gateway
      validation (§6 step 2); the proxy strips standard `X-API-Key`.
- [x] Deploy `pf-svc-reference` and `pf-svc-income` changes with client API-key
      enforcement removed.
- [x] Update income-to-reference calls so local direct calls work without a client key;
      GCP identity-token behavior remains explicit and separate. The GCP call goes
      directly from income to reference and does not traverse the public gateway.
- [x] Update `pf-gateway-proxy` to remove client API-key values before forwarding to
      services.
- [x] Remove API-key validation code, generation, storage, and required settings from
      both services.
- [x] Add tests proving services do not require or inspect client API keys and that
      unrelated authorization remains intact.
- [x] Keep all monetary and domain behavior unchanged; no database migration was added.

## 3. Gateway configuration

- [x] Add native API Gateway API-key security to the sanitized OpenAPI configuration for
      the approved public operations.
- [x] Configure the GCP API/config/gateway resources without committing key values.
- [x] Validate missing and invalid keys at the gateway boundary: missing returned `401`
      and invalid returned `400`. Disabled-key and restricted-key cases remain pending.
- [x] Validate valid-key routing through proxy to both services and preserve status,
      body, `X-Request-ID`, and approved response headers through Postman/GCP traffic.
- [x] Confirm backend business requests cannot bypass gateway validation through a fake
      client-controlled marker header.

## 4. Local and GCP acceptance tests

- [x] Local `pf-svc-reference` direct request succeeds without an API key.
- [x] Local `pf-svc-income` direct request succeeds without an API key.
- [x] Local income-to-reference request succeeds without a client API key.
- [ ] GCP income-to-reference integration is not yet compliant with the approved final
      boundary. The 2026-11-23 log join proved income reached reference successfully and
      preserved `X-Request-ID`, but the deployed income revision still has
      `PF_REFERENCE_URL` pointing to the public gateway facade. It must be changed to the
      direct reference Cloud Run URL, redeployed, and revalidated with a Google identity
      token and no client API key.
- [x] GCP request with a valid gateway key succeeds for approved reference routes.
- [x] GCP request with a valid gateway key succeeds for approved income routes.
- [x] GCP requests with missing and invalid keys are rejected by API Gateway before
      backend business handling. Disabled and unauthorized restriction cases remain
      pending.
- [x] Inspect backend and proxy logs for the successful GCP request: no raw API-key
      value appeared in the inspected entries or response evidence. Gateway rejection
      log coverage remains pending.
- [ ] Verify correlation separately for gateway rejections and successful backend
      requests. Successful income/proxy/reference events shared the supplied
      `X-Request-ID`; rejection behavior still needs a dedicated check.
- [x] Verify direct Cloud Run/IAM behavior remains governed by the
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
- [x] Update Postman collection and environments to separate local no-key requests from
      GCP requests that read a developer-provided secret from Postman Vault or a local
      current value that is never synced. The initial value remains empty and no key is
      committed.
- [x] Add migration notes for clients: the gateway now owns the standard `X-API-Key`
      header, while backend services do not inspect or require it.
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

## 8. Validation evidence

Validated on 2026-11-23 after the standard `X-API-Key` gateway configuration became
`ACTIVE` and the proxy/service deployments completed:

```text
health without key       -> HTTP 200
business without key     -> HTTP 401
business invalid key     -> HTTP 400
business valid key       -> HTTP 200 via Postman/GCP
```

The GCP requests required an approved no-proxy network path; the corporate proxy was
intercepting the gateway hostname through Cisco Umbrella/OpenDNS. The API Gateway
configuration and Postman synchronization both completed successfully. Cloud Logging
also joined income, proxy, and reference events by the supplied request ID, with no raw
API-key value present in the inspected backend/proxy entries.

The `400` for an invalid key is the observed API Gateway behavior and is accepted as the
invalid-key rejection for this implementation. Additional boundary tests on 2026-11-23
found that a revoked test key remained accepted after the configured propagation window
and a test key restricted to `storage.googleapis.com` returned `200` against the PF gateway. Both tests are therefore failed/inconclusive and require investigation before
closure; the temporary test keys were deleted and no raw values were retained.
Service-to-service identity, raw-key log absence, correlation, and rollback evidence
remain separate acceptance items.

## 9. Decision record

**Decision: GO — implementation authorized by `mrturo` on 2026-11-22.**

The approved final state is gateway-owned API-key enforcement for GCP and no API-key
requirement in local direct service execution. Implementation must follow the design
gates, phased rollout, acceptance tests, and rollback procedures defined above.
