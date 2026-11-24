# Brief: active service-name normalization

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: active PF improvement metadata and workflow documentation.  
Related artifacts: investigation.md · recommendation.md · plan.md · evidence/remnant-inventory.md

## Objective

Remove obsolete service-name aliases from active, non-historical improvement metadata and
workflow guidance. Current service identities must be used consistently. The complete approved mapping is:

| Legacy alias | Current identity |
|---|---|
| `pf-payroll` | `pf-svc-income` |
| `pf_payroll` | `pf_svc_income` |
| `pfpayroll` | `pfsvcincome` |
| `pf-rates` | `pf-svc-reference` |
| `pf_rates` | `pf_svc_reference` |
| `pfrates` | `pfsvcreference` |
| `pf-reference` | `pf-svc-reference` |
| `pf_reference` | `pf_svc_reference` |
| `pf-income` | `pf-svc-income` |
| `pf_income` | `pf_svc_income` |

These are aliases used in active documentation or metadata; they are not a request to
rename real repositories or infrastructure resources.

Historical investigations, plans, recommendations, and evidence must remain unchanged
when the old names describe the state or systems that existed at the time. Stable record
IDs, slugs, links, and historical filenames are also not renamed by this task.

## Acceptance criteria

1. Active workflow guidance contains only current service identities.
2. Active improvement metadata uses current service identities for owners, affected
   repositories, and next actions. The `affected` field means current repository
   identities; historical infrastructure names are not rewritten by this task.
3. Historical records retain their original terminology where it is historical evidence.
4. Task-definition and evidence self-references are classified explicitly and do not
   conceal active metadata or workflow remnants.
5. No secrets, credentials, or production data are introduced.
6. Validation passes without manually editing generated outputs.
7. A versioned before/after inventory records every retained historical occurrence,
   task-definition/evidence self-reference, and normalized active occurrence.

## Non-objectives

- Renaming repositories, Cloud Run resources, databases, service accounts, or secrets.
- Rewriting historical evidence merely to make terminology uniform.
- Changing stable historical identifiers or artifact paths.
