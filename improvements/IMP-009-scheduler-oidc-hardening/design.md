# IMP-009 OIDC design and validation matrix

Date: 2026-10-15
Status: validated; implementation and controlled validation complete
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
| OIDC audience | service URL without `/execute` | validated |
| Caller service account | `gcp-scheduler-oidc@coreassistant-474022.iam.gserviceaccount.com` | approved and validated |
| Current invoker grant | `roles/run.invoker` to `allUsers` | removed |
| Target invoker grant | `roles/run.invoker` on `gcp-scheduler-runner` only | validated for the dedicated caller |
| Ingress | `all`; authentication enforced by Cloud Run IAM | validated; no `allUsers` invoker |

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
| Authorized Scheduler OIDC request to `/execute` | HTTP 200 | sanitized Cloud Run log at 2026-10-15T19:06:09Z |
| OIDC token with wrong audience | rejected by Cloud Run/IAM; no operation | status and owner-visible failure record |
| Caller without `roles/run.invoker` | rejected; no operation | status and IAM evidence |
| Expired or malformed token | rejected; no operation | status and failure evidence |
| Correct token, wrong route | normal route error; no unintended operation | status and route evidence |
| Scheduler dispatch after cutover | dispatch accepted; `/execute` returned HTTP 200 with the same OIDC caller | sanitized Scheduler metadata and Cloud Run logs |
| Controlled Scheduler failure | alert/ownership path is observable | status, alert, rollback decision |
| Rollback | OIDC schedule/configuration disabled without restoring exposed key | change record and health check |

Payloads, tokens, authorization headers, secret values, and personal or financial
data must not be copied into the improvement repository.

## 4. Current result

Cloud Scheduler OIDC was validated end-to-end against both `GET /health` and
`POST /execute`. The final controlled dispatch reached `/execute` with HTTP 200
using the dedicated OIDC caller and the service URL audience. The application no
longer requires `X-API-Key` for this route, and the exposed credential was not
restored.

The final workflow run `38798409962` completed `quality-gate`, `deploy`, and
`setup-scheduler` successfully. The orphaned service-account key created during the
failed rotation attempt was deleted after release validation.

## 5. Access and approval gates

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

The read-only inventory and controlled validation gates are complete. Resource, route,
IAM, audience, deployment, Scheduler, and authorized execution checks passed. The
orphaned credential cleanup remains a release-record task; no API-key restoration is
permitted.
