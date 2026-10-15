# IMP-009 OIDC design and validation matrix

Date: 2026-10-15
Status: proposed; implementation not authorized by evidence yet
Scope: Scheduler-to-Cloud Run authentication for `gcp-scheduler-runner`.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)

## 1. Target contract

| Item | Proposed value | Status |
|---|---|---|
| Project | `coreassistant-474022` | observed |
| Region | `us-central1` | observed |
| Scheduler job | `gcp-scheduler-runner-chile` | observed |
| Method | `POST` | observed |
| Route | `/execute` | observed |
| Cloud Run service | `gcp-scheduler-runner` | observed |
| Service URL | `https://gcp-scheduler-runner-yqd4p7fzaa-uc.a.run.app` | observed |
| OIDC audience | service URL without `/execute` | proposed; confirm with service contract |
| Caller service account | dedicated Scheduler-only account, e.g. `gcp-scheduler-oidc@coreassistant-474022.iam.gserviceaccount.com` | proposed; owner must approve exact identity |
| Current invoker grant | `roles/run.invoker` to `allUsers` | observed; public IAM invocation |
| Target invoker grant | `roles/run.invoker` on `gcp-scheduler-runner` only | proposed for the dedicated caller |
| Ingress | current `all`; IAM must stop allowing `allUsers` after cutover | proposed transition |

The audience should identify the Cloud Run service rather than the route. The route
remains part of the HTTP request; the audience is validated by Cloud Run/IAM.
The current Scheduler job includes `X-API-Key` and `X-Scheduler-Trigger` header names;
only the latter may be retained if the route contract requires it. The API-key value
must not be copied, migrated, or restored. Cloud Run currently grants
`roles/run.invoker` to `allUsers`, so removing that public member is a required
cutover step.
Do not reuse the runtime service account
`gcp-scheduler-runner@coreassistant-474022.iam.gserviceaccount.com` as the Scheduler
caller unless ownership and least-privilege review explicitly approve that choice.

## 2. Authentication transition

1. Inventory the current `/execute` authorization behavior without reading or
   recording API-key values. The job metadata confirms an `X-API-Key` header is
   currently configured, while OIDC/OAuth blocks are absent.
2. Confirm the dedicated caller service account and its ownership.
3. Grant only service-level `roles/run.invoker` to that caller while retaining the
   current IAM grant until validation is ready.
4. Configure Scheduler with an OIDC token using the caller account and proposed
   audience.
5. Run authorized, wrong-audience, unauthorized-caller, expired-token, and route
   failure tests against a safe validation window.
6. Observe one Scheduler dispatch and obtain service-side evidence for one successful
   execution and one controlled failure.
7. Remove the `allUsers` invoker member and static API-key dependency only after
   successful evidence and owner approval.

No static API-key fallback is allowed after cutover. Do not make the endpoint
anonymous to compensate for an unverified token configuration.

## 3. Validation matrix

| Case | Expected result | Evidence |
|---|---|---|
| Authorized Scheduler OIDC request to `/execute` | Existing successful operation; no API key | sanitized status, timestamp, revision |
| OIDC token with wrong audience | rejected by Cloud Run/IAM; no operation | status and owner-visible failure record |
| Caller without `roles/run.invoker` | rejected; no operation | status and IAM evidence |
| Expired or malformed token | rejected; no operation | status and failure evidence |
| Correct token, wrong route | normal route error; no unintended operation | status and route evidence |
| Scheduler dispatch after cutover | dispatch accepted by Scheduler; endpoint HTTP outcome separately verified | sanitized dispatch metadata plus approved service-side evidence |
| Controlled Scheduler failure | alert/ownership path is observable | status, alert, rollback decision |
| Rollback | OIDC schedule/configuration disabled without restoring exposed key | change record and health check |

Payloads, tokens, authorization headers, secret values, and personal or financial
data must not be copied into the improvement repository.

## 4. Access and approval gates

Before mutation, obtain all of the following:

- IAM policy for `gcp-scheduler-runner` through an approved VPC Service Controls
  path; **completed** by the sanitized archive, showing `allUsers` currently has
  `roles/run.invoker`;
- exact current authorization behavior for `/execute`, including whether
  `X-Scheduler-Trigger` remains required after IAM authentication;
- owner approval of the dedicated caller service account;
- owner approval of the service URL audience and ingress model;
- an approved validation window and rollback operator;
- confirmation that the legacy API-key path can be removed without changing the
  public API contract.

The current read-only inventory satisfies the resource, route, and IAM discovery
gates. The exact application authorization behavior remains unverified. No IAM,
Scheduler, Cloud Run, or secret mutation is permitted until the remaining approval
and validation gates are recorded as passed.
