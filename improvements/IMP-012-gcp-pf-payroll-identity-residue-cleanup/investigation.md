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

## 3. Safety findings

- Deleting `PF_PAYROLL_DATABASE_URL` is potentially destructive because its values
  were not inspected and its historical consumers are not proven from secret content.
- Removing the deleted-principal IAM member is low risk and should be idempotent.
- Destroying secret versions before deleting the secret is irreversible; owner approval
  and a final consumer inventory are required.
- Cloud Asset Inventory history cannot necessarily be deleted by removing the original
  service accounts or keys.

## 4. Required follow-up evidence

Before mutation:

- search all active Cloud Run revisions and deployment workflows for the secret name;
- inspect Secret Manager IAM without reading values;
- confirm `PF_DATABASE_URL` is the only active runtime database secret;
- confirm no Scheduler, CI, or external integration references the old secret;
- record owner approval for removing the old secret and stale IAM member.

After mutation:

- verify old secret/resource names are absent from active inventories;
- verify `pf-svc-income` health and protected smoke;
- rerun Asset Inventory and classify any remaining historical key records;
- record residual audit-history risk explicitly.
