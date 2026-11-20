# Brief: remove residual `pf-payroll` GCP identity artifacts

Date: 2026-11-20  
Status: in progress
Level: L  
Scope: GCP-only cleanup of residual `pf-payroll`/`pf_payroll` names and access artifacts after HIST-007.
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)
Approved: investigation and low-risk IAM cleanup authorized; destructive secret cleanup pending explicit approval
Superseded-by: none

## Current problem

HIST-007 removed the legacy `pf-payroll` Cloud Run service, Artifact Registry
repository, API key, and service accounts. A read-only GCP inventory still found:

- Secret Manager secret `PF_PAYROLL_DATABASE_URL` with four enabled versions;
- `PF_PAYROLL_DATABASE_URL` access granted to `pf-svc-income` and
  `pf-svc-income-deployer`, plus a deleted `pf-payroll` principal;
- historical service-account-key assets for the deleted
  `pf-payroll@...` and `pf-payroll-deployer@...` identities in Cloud Asset Inventory.

The target runtime contract is `PF_DATABASE_URL`; the active `pf-svc-income` service
references that secret instead. No secret values were read.

## Objective

Remove or normalize every currently actionable GCP artifact whose resource name,
principal, secret, IAM member, or configuration contains `pf-payroll` or
`pf_payroll`, while preserving `pf-svc-income`, `pf-rates`, Scheduler, and the
active database contract.

## Non-objectives

- Do not rename historical audit records that Google Cloud retains by design.
- Do not alter application code, Postman, database schema, or Cloud Run traffic.
- Do not read, copy, rotate, or expose secret values unless separately authorized.
- Do not delete `PF_DATABASE_URL`, `PF_INCOME_API_KEY`, or active service identities.
- Do not remove a secret until all consumers and rollback dependencies are proven absent.

## Acceptance criteria

1. No active Cloud Run service, job, Artifact Registry repository, service account,
   scheduler target, secret reference, or IAM binding contains `pf-payroll` or
   `pf_payroll`.
2. The active service uses only `PF_DATABASE_URL` and `PF_INCOME_API_KEY`.
3. `PF_PAYROLL_DATABASE_URL` is deleted only after consumer inventory and owner
   approval confirm it is unused; otherwise it receives a documented migration plan.
4. Deleted-principal IAM bindings are removed from active resources.
5. Historical Cloud Asset Inventory records are classified as retained audit history
   rather than incorrectly reported as active artifacts.
6. `pf-svc-income` health, protected smoke, and database connectivity remain healthy.
7. Cleanup commands, before/after inventories, and residual-risk decisions are recorded
   without secret values.
