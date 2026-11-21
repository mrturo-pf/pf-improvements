# HIST-007 Execution Authorization Request

**Improvement:** `HIST-007 — pf-svc-income-renaming`  
**Status:** Approved; rollback window closed early on 2026-11-20  
**Prepared by:** `code-puppy-c58a9f`  
**Date:** 2026-11-20

This record requests explicit authorization for the controlled execution phase. It
is not approval by itself. No credentials, production resources, database
migrations, consumer cutovers, commits, pushes, or deployments are authorized by
this document until the applicable approver records approval below.

## Requested authorization scope

| Gate | Scope | Approval required from | Decision |
|---|---|---|---|
| A | Code and package changes in `pf-payroll`, including the approved package-boundary and compatibility work | `mrturo` | Approved |
| B | Reversible `pf-db` migration and the bounded maintenance window | `mrturo` | Approved |
| C | Postman collection and environment target-variable changes | `mrturo` | Approved |
| D | Creation or migration of Artifact Registry, Cloud Run, service account, and secret resources | `mrturo` | Approved |
| E | Consumer cutover and rollback window, including the 14-day minimum retention rule | `mrturo` | Approved |
| F | Commits, pushes, and deployment approvals for each affected repository | `mrturo` | Approved |

## Conditions that apply to every approval

- Use synthetic or explicitly approved operational data for validation.
- Do not expose credentials, tokens, connection strings, or secret values in this
  record, logs, commits, or test fixtures.
- Early closure accepted by `mrturo` on 2026-11-20 despite the absence of a
  production pre-migration snapshot and completed representative monthly flow.
  The old service, image, account, and API key are no longer retained for rollback
  after the cleanup recorded below.
- Stop before mutation if the schema baseline, backup/restore readiness, target URL,
  invoker model, or rollback procedure differs from the approved design.
- Record commit SHAs, workflow/run IDs, migration evidence, smoke-test results, and
  the final rollback/cleanup decision in `plan.md`.
- Approval of one gate does not imply approval of any other gate.

## Approval record

### Gate A — `pf-payroll` code and package changes

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Scope restrictions or conditions:** Conditions in this authorization request apply.
- **Approval reference:** User approval recorded in session

### Gate B — `pf-db` migration and maintenance window

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Approved maintenance window:** Must be scheduled and recorded before mutation.
- **Backup/restore readiness reference:** Must be recorded before mutation.
- **Abort criteria:** Stop on schema, backup, URL, invoker, or rollback mismatch.
- **Approval reference:** User approval recorded in session

### Gate C — Postman changes

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Approved collection/environment scope:** HIST-007 target and environment changes only.
- **Approval reference:** User approval recorded in session

### Gate D — GCP resources and secrets

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Approved resource scope:** HIST-007 resources only, using least privilege.
- **Secret-handling conditions:** Never print or commit secret values.
- **Approval reference:** User approval recorded in session

### Gate E — Consumer cutover and rollback

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Approved cutover window:** Closed early on 2026-11-20 by explicit owner
  acceptance. The 14-day observation period and representative monthly flow were
  waived for this cleanup decision.
- **Rollback owner:** `mrturo` or explicitly delegated operator.
- **Approval reference:** User approval recorded in session

### Gate F — Commits, pushes, and deployments

- **Decision:** Approved
- **Approver:** `mrturo`
- **Date/time:** 2026-11-20 (explicit approval in chat)
- **Repositories and allowed branches:** Affected HIST-007 repositories and dedicated working branches.
- **Deployment/run approval reference:** User approval recorded in session

## Cleanup decision and evidence

The owner explicitly accepted early closure on 2026-11-20 despite the missing
production pre-migration snapshot and incomplete representative monthly flow. The
legacy API key, Cloud Run service, Artifact Registry repository, and legacy runtime
and deployer service accounts were then removed. The new service remained healthy
with 100% traffic and HTTP 200 health response after cleanup.

## Execution stop condition

Phase 3 must not begin until all applicable gates above are recorded as approved
with an approver, timestamp, scope, and reference. A later change in scope requires
an explicit amendment to this record.
