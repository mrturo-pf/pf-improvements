# Recommendation: clean residual `pf-payroll` GCP artifacts

Date: 2026-11-20  
Status: closed
Level: L  
Scope: GCP-only identity and secret residue cleanup.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)
Approved: owner authorized destructive secret cleanup on 2026-11-20
Superseded-by: none

## 1. Recommendation

Use a two-stage cleanup:

1. Remove stale IAM references to deleted `pf-payroll` principals and prove that no
   active resource references `PF_PAYROLL_DATABASE_URL`.
2. After explicit owner approval, disable and destroy all versions of
   `PF_PAYROLL_DATABASE_URL`, then delete the secret.

Do not create a new secret named `PF_SVC_INCOME_DATABASE_URL`; the approved active
contract is the generic `PF_DATABASE_URL`, injected into `pf-svc-income`.

## 2. Decision boundaries

The following are safe read-only or idempotent preparation steps:

- list active resource names and Cloud Run environment references;
- list Secret Manager metadata and IAM bindings without reading values;
- remove IAM bindings whose members are already deleted principals;
- rerun Cloud Asset Inventory after cleanup.

The following require explicit approval immediately before execution:

- disabling or destroying `PF_PAYROLL_DATABASE_URL` versions;
- deleting `PF_PAYROLL_DATABASE_URL`;
- any deletion of a currently active resource discovered during final inventory.

## 3. Alternatives rejected

### Keep the old secret indefinitely

Rejected because it leaves a misleading identity artifact and stale access policy,
contradicting the requested naming invariant.

### Rename by copying secret values automatically

Rejected because it would read or duplicate credentials without a separately approved
secret-rotation/migration procedure. The active service already uses `PF_DATABASE_URL`.

### Delete historical Asset Inventory records

Rejected because audit-history retention is provider-managed and may not be mutable.
Classify such records as historical residual evidence instead.

## 4. Cost and compatibility

- Removing an unused Secret Manager secret and stale IAM binding reduces operational
  confusion without changing active service traffic.
- No new paid resource is required.
- `pf-svc-income`, `pf-rates`, Scheduler, `PF_DATABASE_URL`, and `PF_INCOME_API_KEY`
  must remain unchanged.
- If any active consumer of `PF_PAYROLL_DATABASE_URL` is discovered, stop and create a
  separate migration plan rather than deleting the secret.

## 5. Final decision

The final inventory found no active consumer or resource reference to the old secret.
The owner explicitly authorized cleanup on 2026-11-20. All four versions of
`PF_PAYROLL_DATABASE_URL` were disabled, destroyed, and the secret was deleted.
Active resource inventories are clean. Historical Cloud Asset Inventory records for
old service-account keys remain as provider-retained audit history and are accepted
as the only residual name history.
