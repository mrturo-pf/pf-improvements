# Recommendation: rename `pf-rates` to `pf-svc-financial-data`

Date: 2026-11-20  
Status: proposed  
Level: L  
Scope: Cross-repository financial-data service identity and database-prefix migration.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)
Approved: pending owner approval  
Superseded-by: none

## 1. Executive recommendation

Adopt `pf-svc-financial-data` as the canonical service identity. It accurately covers
exchange rates, monetary units, economic indices, tax brackets, and financial-data
exports without pretending the service only serves rates.

Execute the change as a phased identity and schema migration:

- keep public financial-data route paths stable;
- create parallel GCP resources under `pf-svc-financial-data`;
- migrate consumers to the new URL and `PF_FINANCIAL_DATA_API_KEY`;
- migrate the owned `RAT_*` tables to the approved `FID_*` names through a reversible
  hand-written `pf-db` migration;
- keep implementation package `rates` stable in phase one unless an explicit package
  rename is approved after consumer inventory;
- retain the old service/resources for the full approved rollback/evidence window;
- clean legacy resources only after Go/No-Go, smoke, representative flow, and rollback
  exit criteria are evidenced.

## 2. Canonical identity map

| Current | Target |
|---|---|
| Repository `pf-rates` | `pf-svc-financial-data` |
| Cloud Run service `pf-rates` | `pf-svc-financial-data` |
| Artifact Registry `pf-rates` | `pf-svc-financial-data` |
| Runtime account `pf-rates@...` | `pf-svc-financial-data@...` |
| Deployer account `pf-rates-deployer@...` | `pf-svc-financial-data-deployer@...` |
| `PF_RATES_API_KEY` | `PF_FINANCIAL_DATA_API_KEY` |
| `PF_RATES_URL` | `PF_FINANCIAL_DATA_URL` |
| Postman `pf-rates-url` | `pf-financial-data-url` |
| Postman `pf-rates-api-key` | `pf-financial-data-api-key` |

The database URL decision remains open: converge to the approved generic
`PF_DATABASE_URL` contract, or create a separately approved new database-secret
identity. Do not create `PF_SVC_FINANCIAL_DATA_DATABASE_URL` by default.

## 3. Database decision

Use a reversible migration with this required map:

```text
RAT_CURRENCY   -> FID_RATE_UNIT
RAT_EXCH_RATE  -> FID_RATE_VALUE
RAT_ECON_INDEX -> FID_ECON_INDEX
RAT_TAX_BRCKT  -> FID_TAX_BRCKT
RAT_EXPORT_JOB -> FID_EXPORT_JOB
```

The first two mappings are owner-specified semantic names. The remaining mappings
apply the `FID_` prefix while preserving existing suffix vocabulary and minimizing
unnecessary contract changes. The final map requires explicit approval before code
or migration implementation.

The migration must preserve:

- primary/foreign keys and indexes;
- sequences and constraints under the identifier-length policy;
- export-job lifecycle and status values;
- grants and runtime role boundaries;
- row counts and aggregate values;
- `pf-svc-income` HTTP behavior and API-key consumers.

## 4. Rejected approaches

### Blind global replacement

Rejected. It would rename domain terms, route paths, Python modules, and historical
references indiscriminately and could break consumers or audit history.

### In-place Cloud Run/Artifact Registry rename

Rejected. These resources require parallel deployment and explicit traffic cutover.

### Service-specific database-secret alias by default

Rejected. HIST-007/IMP-012 showed that aliases create stale identity residue. Use the
approved generic `PF_DATABASE_URL` unless a separate database-credential decision
requires otherwise.

### Early rollback closure by default

Rejected. HIST-007 closed early only after explicit owner waiver; IMP-013 should
require the full evidence window unless the owner records the same type of waiver.

## 5. Compatibility and cost

- Public route compatibility is preserved.
- `pf-svc-income` continues HTTP consumption; it must not gain direct `FID_*` reads.
- Parallel Cloud Run and Artifact Registry resources create temporary duplication
  cost; keep scale-to-zero and delete old resources only after the approved window.
- No paid scanning or always-on compute should be introduced.
