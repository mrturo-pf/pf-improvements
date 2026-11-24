# Brief: active service-name normalization

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: active PF improvement metadata and workflow documentation.  
Related artifacts: investigation.md · recommendation.md · plan.md

## Objective

Remove obsolete service-name aliases from active, non-historical improvement metadata and
workflow guidance. Current service identities must be used consistently:

- income service: `pf-svc-income`
- reference service: `pf-svc-reference`
- Compact income identity: `pfsvcincome`
- Python-style reference identity: `pf_svc_reference`
- Compact reference identity: `pfsvcreference`

Historical investigations, plans, recommendations, and evidence must remain unchanged
when the old names describe the state or systems that existed at the time. Stable record
IDs, slugs, links, and historical filenames are also not renamed by this task.

## Acceptance criteria

1. Active workflow guidance contains only current service identities.
2. Active improvement metadata uses current service identities for owners, affected
   repositories, and next actions.
3. Historical records retain their original terminology where it is historical evidence.
4. No secrets, credentials, or production data are introduced.
5. Validation passes without manually editing generated outputs.
6. A before/after inventory records every retained historical occurrence and every
   normalized active occurrence.

## Non-objectives

- Renaming repositories, Cloud Run resources, databases, service accounts, or secrets.
- Rewriting historical evidence merely to make terminology uniform.
- Changing stable historical identifiers or artifact paths.
