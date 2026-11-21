# Investigation: Scheduler OIDC hardening

Date: 2026-10-12
Status: validated
Level: M
Scope: Replace static Scheduler API-key authentication with least-privilege OIDC authentication after separate design and validation.
Owner: `pf-payroll`
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [design](design.md) · [plan](plan.md) · [IMP-001 source](../HIST-008-gcp-scheduler-credential-exposure/investigation.md) · [register](../../index.md)
Superseded-by: none

## 1. Question

Can the Scheduler-to-service invocation path use a dedicated OIDC identity and
least-privilege audience/permission model, eliminating the static API key without
breaking scheduled operations or creating an implicit public endpoint?

## 2. Known boundary

`IMP-001` remediation is released: the exposed API key was contained, rotated or
removed as applicable, and the residual historical logging limitation was accepted.
OIDC is a separate hardening decision and must not be represented as unfinished
incident response.

The investigation must verify the actual Scheduler job, target URL, service
invocation policy, current caller identity, API route, environment, and rollback
path before designing a mutation. No credential value may be read or recorded.

## 3. Evidence required

- Scheduler job metadata and target authentication configuration;
- Cloud Run service IAM/invocation policy and environment;
- dedicated caller service account ownership and existing grants;
- exact OIDC audience and token subject requirements;
- target route behavior and API error contract;
- rollback path that does not reintroduce a long-lived shared key.

Use sanitized resource names, roles, URLs where safe, status codes, and hashes or
metadata only. Do not record tokens, headers, secret values, or real payloads.

## 4. Open questions

1. Is the target endpoint suitable for OIDC without changing public API semantics?
2. Should the Scheduler caller invoke a private Cloud Run service or an authenticated
   public endpoint with invoker permission?
3. What audience and service-account ownership are approved?
4. How is a failed scheduled execution detected and rolled back safely?

## 5. Read-only inventory (2026-10-15)

A sanitized read-only inventory was collected for project `coreassistant-474022` and
region `us-central1`. No Scheduler, IAM, Cloud Run, secret, or API mutation was
performed.

| Resource | Observed value | Evidence boundary |
|---|---|---|
| Scheduler job | `gcp-scheduler-runner-chile` | enabled; metadata only |
| Schedule | `30 4 * * *` UTC | job metadata |
| Method and target | `POST https://gcp-scheduler-runner-yqd4p7fzaa-uc.a.run.app/execute` | URI and method only |
| Scheduler OIDC/OAuth metadata | not present; HTTP headers include `X-API-Key` and `X-Scheduler-Trigger` | names only; values and body were not read |
| Cloud Run service | `gcp-scheduler-runner` | service metadata |
| Cloud Run ingress | `all` | service annotation |
| Cloud Run max scale | `20` | service annotation |
| Runtime service account | `gcp-scheduler-runner@coreassistant-474022.iam.gserviceaccount.com` | revision template metadata |
| Cloud Run IAM policy | `roles/run.invoker` granted to `allUsers` | sanitized policy archive; service is publicly invocable at IAM level |

The target is the standalone `gcp-scheduler-runner` service, not `pf-payroll`.
The current job structurally depends on an `X-API-Key` header; its value was not read
or recorded. Cloud Run also grants `roles/run.invoker` to `allUsers`, so IAM currently
allows public invocation and the API key is an application-level control. The current
evidence was sufficient to refine and execute the controlled cutover. The caller
identity and IAM transition were approved through the phase confirmations. The IAM
policy is now known: the cutover uses only the dedicated caller. Final service-side
execution evidence is recorded below.

## 6. Phase 1 and phase 2 result

The approved controlled phases applied the dedicated OIDC caller and removed the public
IAM member and legacy Scheduler API-key header. The sanitized phase 2 evidence shows
`roles/run.invoker` only for the dedicated caller and OIDC configured with the approved
audience. Scheduler accepted a controlled dispatch. The service-side OIDC probe reached
`GET /health` with HTTP `200`, proving the caller, audience, and Cloud Run IAM path work.
After the route authorization update, a production `POST /execute` dispatch reached
Cloud Run with HTTP `200` at 2026-10-15T19:06:09Z. The final workflow run `38798409962`
completed all three jobs successfully.

## 7. Current conclusion

The read-only inventory, IAM/OIDC cutover, service route update, deployment, Scheduler
configuration, and controlled `/execute` dispatch are complete. The final run
`38798409962` passed `quality-gate`, `deploy`, and `setup-scheduler`. Scheduler is
enabled with the dedicated OIDC caller and `/execute` returned HTTP 200 without the
legacy API key.

IMP-009 is released. The orphaned service-account key created during the failed
rotation attempt was deleted, and the active keys used by `GCP` and `GCP-Auto` were
verified to be the only remaining user-managed keys.
