# Brief: rename `pf-rates` to `pf-svc-financial-data`

Date: 2026-11-20  
Status: approved for execution
Level: L  
Scope: Cross-repository service identity rename, GCP migration, consumer migration, and `RAT_* → FID_*` database migration.
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)
Approved: 2026-11-20 by `mrturo` (conversation)
Superseded-by: none

## Objective

Rename the financial reference-data service from `pf-rates` to
`pf-svc-financial-data` across the PF ecosystem and migrate its owned database
objects from the `RAT_*` prefix to `FID_*`.

The target service covers more than exchange rates:

- exchange-rate values;
- monetary/rate units including currencies and UF/UTM;
- economic indices such as IPC;
- Chilean income-tax brackets;
- asynchronous financial-data exports.

The HTTP route vocabulary and domain behavior should remain stable unless a
separate contract decision approves a route change.

## Required schema changes

The approved explicit mappings are:

| Current object | Target object |
|---|---|
| `RAT_CURRENCY` | `FID_RATE_UNIT` |
| `RAT_EXCH_RATE` | `FID_RATE_VALUE` |
| `RAT_ECON_INDEX` | `FID_ECON_INDEX` |
| `RAT_TAX_BRCKT` | `FID_TAX_BRCKT` |
| `RAT_EXPORT_JOB` | `FID_EXPORT_JOB` |

The first two mappings are semantic renames supplied by the owner. The remaining
objects preserve their suffix while adopting the `FID_` service prefix. The complete
map is approved for implementation.

## Ecosystem scope

- `pf-rates` repository, local folder, distribution, package/build identity, and docs;
- `pf-db` schema, seeds, Alembic migrations, grants, indexes, views, and ownership docs;
- `pf-common` workflow templates, dependency synchronization, and deployment examples;
- `pf-svc-income` dependency URL, client configuration, and API-key secret access;
- `pf-postman` collection folders and LOCAL/GCP environment variables;
- `pf-sheets` consumer inventory and any live endpoint configuration;
- root architecture, generated context, and coordination artifacts;
- GCP Cloud Run, Artifact Registry, runtime/deployer accounts, secrets, IAM, and URLs.

## Non-objectives

- No change to `/economic-indices/*`, `/exchange-rates/*`, `/income-tax-brackets/*`,
  `/monetary-units`, or other public routes unless separately approved.
- No redesign of financial calculation behavior.
- No direct database access by `pf-svc-income`; it continues to consume the HTTP API.
- The financial-data service database secret target is `PF_FINANCIAL_DATA_DATABASE_URL`;
  it remains separate from `PF_DATABASE_URL` used by `pf-svc-income`.
- No secret-value copying into Git, Postman committed JSON, or generated artifacts.
- No early rollback closure by default; the evidence window must be completed or
  explicitly waived by the owner before cleanup.

## Acceptance criteria

1. No active artifact or configuration contains the old service identity
   `pf-rates`, `PF_RATES`, or `pf_rates` where it denotes the service identity.
2. Active identity names use `pf-svc-financial-data`, `PF_FINANCIAL_DATA`, or
   `pf_financial_data` as appropriate.
3. The reversible `RAT_* → FID_*` migration passes upgrade/downgrade, catalog,
   row-count, foreign-key, index, grant, and aggregate validation.
4. `pf-svc-income`, `pf-sheets`, Postman, and all other consumers use the new URL
   and API-key contract before old resources are removed.
5. A complete backup/snapshot, drain record, Go/No-Go decision, smoke evidence,
   and representative financial-data flow are recorded before cleanup.
6. Cloud Asset Inventory residual history is classified separately from active
   resources, as learned in IMP-012.
