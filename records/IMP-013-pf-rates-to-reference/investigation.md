# Investigation: rename `pf-rates` to `pf-svc-reference`

Date: 2026-11-20  
Status: completed
Level: L  
Scope: Service identity, consumers, GCP resources, Postman, shared tooling, and `RAT_* → REF_*` schema ownership.
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)
Approved: investigation preparation only  
Superseded-by: none

## 1. Current service responsibility

`pf-rates` is a FastAPI microservice for Chilean financial reference data, not only
exchange rates. Its documented responsibilities include:

- exchange rates from Mindicador and BCCH;
- monetary units and economic indices such as UF, UTM, and IPC;
- income-tax brackets;
- spreadsheet/export-job operations;
- PostgreSQL persistence owned by `pf-db`.

`pf-svc-income` calls it over HTTP using the current `PF_RATES_URL` and
`PF_RATES_API_KEY` contract. `pf-sheets` synchronizes exchange-rate data and
Postman catalogs the service endpoints.

## 2. Existing naming inventory

The current identity appears in:

- repository and local checkout: `pf-rates`;
- Cloud Run service and Artifact Registry repository: `pf-rates`;
- runtime and deployer service accounts: `pf-rates@...` and `pf-rates-deployer@...`;
- API key and database-secret names: `PF_RATES_API_KEY`, `PF_RATES_DATABASE_URL`;
- consumer URL/key variables: `PF_RATES_URL`, `pf-rates-url`, `pf-rates-api-key`;
- shared workflow/dependency configuration and root architecture/docs;
- internal Python package/module names such as `rates` and `pf_rates_client`.

The migration must distinguish service identity from stable financial-domain terms.
The initial recommendation is to rename service/resource identity while preserving
public route names and internal domain package names unless a separate decision
proves that they are identity leaks.

## 3. Current database ownership

`pf-db` currently owns five rates-domain tables:

```text
RAT_CURRENCY
RAT_EXCH_RATE
RAT_ECON_INDEX
RAT_TAX_BRCKT
RAT_EXPORT_JOB
```

The proposed target map is:

```text
RAT_CURRENCY  -> REF_RATE_UNIT
RAT_EXCH_RATE -> REF_RATE_VALUE
RAT_ECON_INDEX -> REF_ECON_INDEX
RAT_TAX_BRCKT -> REF_TAX_BRCKT
RAT_EXPORT_JOB -> REF_EXPORT_JOB
```

`RAT_EXCH_RATE.currency_code` references `RAT_CURRENCY.code`; the migration must
preserve this relationship as `REF_RATE_VALUE.currency_code` referencing
`REF_RATE_UNIT.code`. Seeds, indexes, constraints, sequences, views, grants,
export-job code, tests, and documentation must be inventoried from the actual
schema rather than renamed with a blind string replacement.

## 4. GCP and secret lessons from HIST-007/IMP-012

- Create parallel resources before cutover; do not rename Cloud Run or Artifact
  Registry in place.
- Use immutable image digests and verify the ready revision before moving traffic.
- Use the approved generic database contract `PF_DATABASE_URL`; do not create a
  service-specific database-secret alias such as `PF_SVC_REFERENCE_DATABASE_URL`.
- Use a new service API key, expected target name `PF_REFERENCE_API_KEY`,
  with an atomic consumer cutover.
- Remove old IAM bindings before secret destruction, and verify active consumers first.
- Treat Cloud Asset Inventory records for deleted service-account keys as retained
  audit history, not active resources.
- Do not close the rollback window early unless the owner explicitly accepts every
  missing evidence item.

## 5. Required evidence before implementation

- complete consumer and repository inventory;
- exact GCP resource and secret inventory without reading secret values;
- `pf-db` object/dependency/grant inventory;
- sanitized pre-migration backup metadata and schema/count snapshot;
- reversible migration design with explicit lock, drain, rollback, and abort criteria;
- Postman LOCAL/GCP variable migration plan;
- Go/No-Go checklist and representative financial-data flow;
- cost/compatibility impact for parallel Cloud Run and Artifact Registry resources.

## 6. Decisions recorded (2026-11-20)

1. Canonical identity: `pf-svc-reference`.
2. API key target: `PF_REFERENCE_API_KEY`.
3. Database secret target: `PF_REFERENCE_DATABASE_URL`, separate from
   `PF_DATABASE_URL` used by `pf-svc-income`.
4. Complete `RAT_* → REF_*` map approved as listed in the brief.
5. Internal Python package `rates` remains unchanged in phase one.
6. Migration, cutover, rollback, and cleanup execution authorized by `mrturo`.

The execution plan must still capture the concrete maintenance window, backup
metadata, Go/No-Go record, and final evidence before destructive cleanup.
