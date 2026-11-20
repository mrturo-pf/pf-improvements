# Plan: remove residual `pf-payroll` GCP identity artifacts

Date: 2026-11-20  
Status: closed
Level: L  
Scope: GCP resource-name, Secret Manager, IAM, and audit-residue cleanup.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)
Approved: investigation and cleanup approved by owner on 2026-11-20
Superseded-by: none

## 1. Gates

- [x] Read-only project and region inventory completed.
- [x] Active Cloud Run, jobs, Artifact Registry, service-account, and Scheduler names checked.
- [x] Secret Manager names, versions, and IAM checked without reading values.
- [x] Historical Cloud Asset Inventory residue identified and classified as a separate concern.
- [x] Search deployment workflows and active service revisions for `PF_PAYROLL_DATABASE_URL`; no active references found.
- [x] Confirm no local repository/module/workflow consumer uses `PF_PAYROLL_DATABASE_URL`; external consumer proof remains limited to GCP metadata.
- [x] Remove stale IAM member for the deleted `pf-payroll` principal.
- [x] Approve disabling and destroying old secret versions.
- [x] Disable/destroy old secret versions.
- [x] Approve deleting `PF_PAYROLL_DATABASE_URL`.
- [x] Delete `PF_PAYROLL_DATABASE_URL`.
- [x] Verify no active artifact name contains `pf-payroll` or `pf_payroll`.
- [x] Verify `pf-svc-income` health, protected smoke, and database connectivity.
- [x] Re-run Cloud Asset Inventory and document retained historical records.

## 2. Execution order

### Phase 1 — Read-only reference inventory

1. Search local repositories, workflows, Cloud Run revisions, and Scheduler targets
   for `PF_PAYROLL_DATABASE_URL`, `pf-payroll`, and `pf_payroll`.
2. Confirm the active service uses only `PF_DATABASE_URL` and `PF_INCOME_API_KEY`.
3. Record secret IAM members without reading secret values.

### Phase 2 — Low-risk IAM cleanup

1. Remove only the deleted `pf-payroll` principal from `PF_PAYROLL_DATABASE_URL`
   IAM, if the binding remains and no active identity uses it.
2. Verify active service health and protected smoke.
3. Stop if any live resource still references the old secret/name.

### Phase 3 — Secret retirement

1. Record owner approval for destructive secret cleanup.
2. Disable all old secret versions and verify no active workload fails.
3. Destroy old versions and delete `PF_PAYROLL_DATABASE_URL`.
4. Verify `PF_DATABASE_URL` remains active and unchanged.

### Phase 4 — Final inventory and closure

1. Search active GCP resources again for both spelling variants.
2. Verify `pf-svc-income`, `pf-rates`, and Scheduler health.
3. Re-run Cloud Asset Inventory.
4. Classify provider-retained deleted-key records as historical audit evidence if they
   remain; do not claim provider history was deleted.
5. Record command/run IDs, timestamps, and residual risk without secret values.

## 3. Safety rules

- Never print, export, compare, or copy secret values.
- Do not delete `PF_DATABASE_URL` or `PF_INCOME_API_KEY`.
- Do not rename the active Cloud Run service or Artifact Registry repository.
- Do not delete historical audit records by unsupported means.
- Stop on any active consumer or unexpected resource reference.

## 4. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-11-20 | investigating | Found `PF_PAYROLL_DATABASE_URL` with four enabled versions and stale access for a deleted `pf-payroll` principal. Cloud Asset Inventory also retains historical keys for deleted legacy accounts. No mutation performed. | Read-only GCP inventory |
| 2026-11-20 | validating | Confirmed no active GCP resource name or Cloud Run revision references `pf-payroll`, `pf_payroll`, or `PF_PAYROLL_DATABASE_URL`; active modules/workflows also contain no `PF_PAYROLL_DATABASE_URL` reference. Removed the deleted `pf-payroll` principal from the old secret's IAM policy. The secret and all four versions remain pending owner-approved destruction. | Targeted GCP inventory; repository scan; Secret Manager IAM removal |
| 2026-11-20 | closed | Owner authorized and completed disable/destroy/delete of all four `PF_PAYROLL_DATABASE_URL` versions and the secret. Active secrets/resources/accounts contain no `pf-payroll` or `pf_payroll`; `pf-svc-income-00012-kdr` remained at 100% traffic and health returned HTTP 200. Cloud Asset Inventory still returns two historical deleted service-account-key records; these are retained audit history, not active artifacts. | GCP cleanup commands; absence checks; health smoke; Asset Inventory post-cleanup query |
