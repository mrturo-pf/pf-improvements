# Investigation: Scheduler OIDC hardening

Date: 2026-10-12
Status: investigating
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
evidence is sufficient to refine the design target but not to approve
or execute the cutover. The caller identity, current authentication header behavior, and exact route
authorization contract still require an owner decision. The IAM policy is now
known: the cutover must add a dedicated caller before removing `allUsers`.

## 6. Current conclusion

The read-only inventory is partially complete and the OIDC design remains pending
explicit owner approval. The proposed design and validation matrix are recorded in [design.md](design.md).
It targets the standalone `gcp-scheduler-runner` service, its `/execute` route, a
dedicated Scheduler caller, and a precise Cloud Run audience. Do not mutate Scheduler, IAM, Cloud Run ingress,
or API-key configuration until the design is explicitly approved.
