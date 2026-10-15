# Plan: Scheduler OIDC hardening

Date: 2026-10-12
Status: released
Level: M
Scope: Replace static Scheduler API-key authentication with least-privilege OIDC authentication.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md) · [design](design.md)
Approved: 2026-10-15; owner-confirmed controlled execution
Superseded-by: none

## 1. Gates

- [x] `IMP-001` containment/remediation is released and treated as a completed prerequisite.
- [x] Scheduler job, Cloud Run target, and current IAM policy inventoried; current route authorization behavior remains unverified.
- [x] Brief, recommendation, and proposed design approved for controlled execution.
- [x] Caller identity and resource-level IAM model applied: dedicated caller with service-level invoker grant.
- [x] Audience, route, environment, and ingress cutover applied; public `allUsers` access removed.
- [x] Cloud Scheduler OIDC reached `/health` with HTTP 200 and the updated `/execute` route returned HTTP 200.
- [x] Authorized `/execute` validation passed; unauthenticated access was rejected before the final cutover and IAM is restricted to the dedicated caller.
- [x] Legacy API-key header removed; rollback does not restore a credential.

## 2. Implementation slices

### Slice 1 — Read-only inventory

Record sanitized Scheduler job, target service, environment, route, IAM, ingress,
and current authentication metadata. Do not read secret values or tokens.

### Slice 2 — Design validation

Confirm caller service-account ownership, audience, invoker scope, route behavior,
failure handling, and rollback without mutation using [design.md](design.md).

### Slice 3 — Controlled implementation

After explicit approval, create/update only the required resource-level IAM and
Scheduler configuration. Validate authorized and unauthorized synthetic requests.

### Slice 4 — Cutover and closure

Observe a scheduled execution, remove the legacy static-key path, retain evidence,
and update the register/index. Do not delete rollback resources until the approved
window closes.

## 3. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-10-12 | investigating | Promoted IMP-009 to formal artifacts; no Scheduler, IAM, Cloud Run, or secret mutation. | IMP-001 release record and register |
| 2026-10-15 | investigating | Collected sanitized Scheduler and Cloud Run metadata; confirmed header names include `X-API-Key` and `X-Scheduler-Trigger`, no OIDC/OAuth block, and `allUsers` has `roles/run.invoker`. No mutation. | [investigation](investigation.md#5-read-only-inventory-2026-10-15) · [design](design.md) |
| 2026-10-15 | investigating | Phase 1 and phase 2 applied: dedicated OIDC caller granted `roles/run.invoker`, Scheduler audience configured, `allUsers` removed, and `X-API-Key` removed. `/health` returned 200 through Scheduler OIDC, while `/execute` returned 401 and needs a target-service contract change. | Sanitized phase 2 and OIDC health archives |
| 2026-10-15 | validated | Updated `gcp-scheduler-runner` to rely on the Cloud Run IAM boundary for `/execute`; rotated the GitHub Actions credentials for both deployment environments; synchronized `GCP_PROJECT_ID`; and made Scheduler setup validation portable and idempotent. A controlled Scheduler dispatch reached `/execute` with HTTP 200. | Commits `ca904d9`, `a07a2d1`, `82fb14c`, `8002066`, `868e693`; runs `38788025690`, `38798409962` |
| 2026-10-15 | released | Deleted orphaned key `893f1c20d78ccc2dc042586de31a4cb05410f88d`; verified only the active `GCP` and `GCP-Auto` keys remain. | Sanitized Cloud Shell command output |

## 4. Release record

- Commits: `ca904d9`, `a07a2d1`, `82fb14c`, `8002066`, `868e693`
- Workflow run: `38798409962` — `quality-gate`, `deploy`, and `setup-scheduler` all successful
- Owner approval: confirmed through controlled execution on 2026-10-15
- IAM/Scheduler mutation: dedicated OIDC caller, resource-level invoker, `actAs` and viewer grants applied; public `allUsers` invoker removed
- Scheduled execution evidence: Cloud Scheduler dispatch reached `POST /execute` with HTTP 200; Scheduler remains enabled
- Rollback evidence: no credential restoration path; dedicated invoker rollback documented
- Credential cleanup: orphaned key `893f1c20d78ccc2dc042586de31a4cb05410f88d` deleted; only active environment keys `1c5ef190...` (`GCP`) and `c6441335...` (`GCP-Auto`) remain
- Remaining implementation: none; technical release complete
