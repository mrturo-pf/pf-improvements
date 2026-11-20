# Investigation: residual `pf-payroll` GCP identity artifacts

Date: 2026-11-20  
Status: validating
Level: L  
Scope: GCP resource names, Secret Manager, IAM, and Cloud Asset Inventory.
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md)
Approved: investigation and low-risk IAM cleanup authorized; destructive secret cleanup pending
Superseded-by: none

## 1. Question

Which currently actionable GCP artifacts still contain `pf-payroll` or
`pf_payroll`, and can they be safely removed or normalized to the
`pf-svc-income`/`pf_svc_income` identity without affecting active workloads?

## 2. Read-only inventory

Project and region:

```text
project: coreassistant-474022
region: us-central1
```

### Active resource names

No active resources matching `pf-payroll` or `pf_payroll` were found in the
following targeted inventories:

- Cloud Run services;
- Cloud Run jobs;
- Artifact Registry repositories;
- service-account email list;
- Cloud Scheduler job names;
- active Cloud Run environment references.

Active PF services are `pf-rates` and `pf-svc-income`.

### Residual Secret Manager artifact

```text
Secret: PF_PAYROLL_DATABASE_URL
Versions: 1, 2, 3, 4 — enabled
```

The secret IAM policy currently includes:

```text
serviceAccount:pf-svc-income@coreassistant-474022.iam.gserviceaccount.com
serviceAccount:pf-svc-income-deployer@coreassistant-474022.iam.gserviceaccount.com
deleted:serviceAccount:pf-payroll@coreassistant-474022.iam.gserviceaccount.com
```

The active `pf-svc-income` Cloud Run revision references `PF_DATABASE_URL`, not
`PF_PAYROLL_DATABASE_URL`. The secret values were not read, so content equivalence
has not been assumed.

### Historical Cloud Asset Inventory records

Cloud Asset Inventory returned historical `ServiceAccountKey` records for:

```text
pf-payroll@coreassistant-474022.iam.gserviceaccount.com
pf-payroll-deployer@coreassistant-474022.iam.gserviceaccount.com
```

The corresponding service accounts are absent from the active service-account list
and were deleted by HIST-007. These records may be retained audit history and must
not be treated as active identities without a current IAM/resource reference.

## 3. Final evidence and closure

Before mutation, active Cloud Run revisions, local modules/workflows, Secret Manager IAM,
and resource names were checked without reading secret values. No active consumer of
`PF_PAYROLL_DATABASE_URL` was found.

After mutation:

- `PF_PAYROLL_DATABASE_URL` and all four versions were deleted;
- active secrets, services, repositories, accounts, and Scheduler names contain no
  `pf-payroll` or `pf_payroll` residue;
- `pf-svc-income` remained healthy at 100% traffic and `/health` returned HTTP 200;
- Cloud Asset Inventory still returns two historical deleted service-account-key
  records. They are provider-retained audit history, not active artifacts, and are
  documented as accepted residual history.

IMP-012 is closed. No secret values were read or committed.
