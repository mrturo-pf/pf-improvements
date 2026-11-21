# IMP-013 Execution Authorization

**Improvement:** `IMP-013 — pf-rates-to-pf-svc-financial-data`  
**Status:** Approved for execution  
**Approver:** `mrturo`  
**Date:** 2026-11-20

The owner explicitly approved the decisions below. This record authorizes the
planned execution scope, but each destructive production action still requires the
plan's validation gates and evidence before cleanup.

## Approved decisions

| Gate | Decision | Status |
|---|---|---|
| Canonical service identity | `pf-svc-financial-data` | Approved |
| API key | `PF_FINANCIAL_DATA_API_KEY` | Approved |
| Database secret | `PF_FINANCIAL_DATA_DATABASE_URL`, separate from `PF_DATABASE_URL` used by `pf-svc-income` | Approved |
| Database map | `RAT_CURRENCY → FID_RATE_UNIT`; `RAT_EXCH_RATE → FID_RATE_VALUE`; `RAT_ECON_INDEX → FID_ECON_INDEX`; `RAT_TAX_BRCKT → FID_TAX_BRCKT`; `RAT_EXPORT_JOB → FID_EXPORT_JOB` | Approved |
| Python package | Preserve internal `rates` package in phase one | Approved |
| Execution | Migration, cutover, rollback window, commits, pushes, deployments, and cleanup | Approved |

## Required conditions

- No secret values may enter Git, Postman JSON, generated artifacts, or logs.
- The reversible migration must pass upgrade/downgrade and schema/data invariants.
- Backup metadata, pre-migration snapshot, drain record, Go/No-Go, smoke results,
  and representative financial-data flow must be recorded before cleanup.
- Legacy resources and secrets must remain available for the approved rollback window
  unless the owner records an explicit early-closure waiver.
- Cloud Asset Inventory records for deleted resources must be classified as historical
  audit evidence if the provider retains them.
- `pf-svc-income` must continue using `PF_DATABASE_URL` and its own API key contract.

## Approval reference

Owner approval was provided in the coding session on 2026-11-20. No GCP, database,
secret, repository, or consumer mutation has been performed for IMP-013 by this
authorization record alone.
