# Recommendation: rename `pf-rates` to `pf-svc-reference`

Date: 2026-11-20  
Status: observation
Level: L  
Scope: Cross-repository financial-data service identity and database-prefix migration.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [plan](plan.md)
Approved: 2026-11-20 by `mrturo` (conversation)
Superseded-by: none

## 1. Executive recommendation

Adopt `pf-svc-reference` as the canonical service identity. It accurately covers
exchange rates, monetary units, economic indices, tax brackets, and financial-data
exports without pretending the service only serves rates.

Execute the change as a phased identity and schema migration:

- keep public financial-data route paths stable;
- create parallel GCP resources under `pf-svc-reference`;
- migrate consumers to the new URL and `PF_REFERENCE_API_KEY`;
- migrate the owned `RAT_*` tables to the approved `REF_*` names through a reversible
  hand-written `pf-db` migration;
- keep implementation package `rates` stable in phase one unless an explicit package
  rename is approved after consumer inventory;
- retain the old service/resources for the full approved rollback/evidence window;
- clean legacy resources only after Go/No-Go, smoke, representative flow, and rollback
  exit criteria are evidenced.

## 2. Canonical identity map

| Current | Target |
|---|---|
| Repository `pf-rates` | `pf-svc-reference` |
| Cloud Run service `pf-rates` | `pf-svc-reference` |
| Artifact Registry `pf-rates` | `pf-svc-reference` |
| Runtime account `pf-rates@...` | `pf-svc-reference@...` |
| Deployer account `pf-rates-deployer@...` | `pf-svc-reference-deployer@...` |
| `PF_RATES_API_KEY` | `PF_REFERENCE_API_KEY` |
| `PF_RATES_URL` | `PF_REFERENCE_URL` |
| Postman `pf-rates-url` | `pf-reference-url` |
| Postman `pf-rates-api-key` | `pf-reference-api-key` |

Use the separately named database secret `PF_REFERENCE_DATABASE_URL` for
`pf-svc-reference`; do not converge it to `PF_DATABASE_URL`, which remains the
approved runtime contract for `pf-svc-income`.

## 3. Database decision

Use a reversible migration with this required map:

```text
RAT_CURRENCY   -> REF_RATE_UNIT
RAT_EXCH_RATE  -> REF_RATE_VALUE
RAT_ECON_INDEX -> REF_ECON_INDEX
RAT_TAX_BRCKT  -> REF_TAX_BRCKT
RAT_EXPORT_JOB -> REF_EXPORT_JOB
```

The first two mappings are owner-specified semantic names. The remaining mappings
apply the `REF_` prefix while preserving existing suffix vocabulary and minimizing
unnecessary contract changes. The final map is approved for code and migration implementation.

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
- `pf-svc-income` continues HTTP consumption; it must not gain direct `REF_*` reads.
- Parallel Cloud Run and Artifact Registry resources create temporary duplication
  cost; keep scale-to-zero and delete old resources only after the approved window.
- No paid scanning or always-on compute should be introduced.
