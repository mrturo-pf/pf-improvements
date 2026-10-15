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
- [~] Scheduler job and Cloud Run target inventory collected; IAM policy and current header authorization remain blocked by VPC Service Controls/approval.
- [ ] Brief, recommendation, and proposed design approved.
- [ ] Caller identity and resource-level IAM model approved.
- [ ] Audience, route, environment, and ingress contract approved.
- [ ] Synthetic authorized/unauthorized validation passed.
- [ ] One scheduled execution and failure case observed.
- [ ] Legacy API-key path removed with rollback evidence.

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
| 2026-10-15 | investigating | Collected sanitized Scheduler and Cloud Run metadata; IAM policy lookup was blocked by VPC Service Controls. No mutation. | [investigation](investigation.md#5-read-only-inventory-2026-10-15) |

## 4. Release record

- Commits: pending
- Workflow runs: pending
- Owner approval: pending
- IAM/Scheduler mutation: pending
- Scheduled execution evidence: pending
- Rollback evidence: pending
