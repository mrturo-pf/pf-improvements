# Plan: Scheduler OIDC hardening

Date: 2026-10-12
Status: investigating
Level: M
Scope: Replace static Scheduler API-key authentication with least-privilege OIDC authentication.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md) · [design](design.md)
Approved: pending explicit owner approval
Superseded-by: none

## 1. Gates

- [x] `IMP-001` containment/remediation is released and treated as a completed prerequisite.
- [x] Scheduler job, Cloud Run target, and current IAM policy inventoried; current route authorization behavior remains unverified.
- [ ] Brief, recommendation, and proposed design approved.
- [x] Caller identity and resource-level IAM model applied: dedicated caller with service-level invoker grant.
- [x] Audience, route, environment, and ingress cutover applied; public `allUsers` access removed.
- [ ] Synthetic authorized/unauthorized validation passed with service-side evidence.
- [~] Scheduler dispatch accepted after cutover; endpoint result and failure case still require service-side evidence.
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
| 2026-10-15 | investigating | Phase 1 and phase 2 applied: dedicated OIDC caller granted `roles/run.invoker`, Scheduler audience configured, `allUsers` removed, and `X-API-Key` removed. Scheduler dispatch was accepted; endpoint outcome remains unverified because Cloud Logging/service evidence is still required. | Sanitized phase 2 archive |

## 4. Release record

- Commits: pending
- Workflow runs: pending
- Owner approval: phase execution confirmed interactively; formal design closure pending
- IAM/Scheduler mutation: phase 1 and phase 2 applied
- Scheduled execution evidence: dispatch accepted; service-side HTTP outcome pending
- Rollback evidence: no credential restoration path; dedicated invoker rollback documented
