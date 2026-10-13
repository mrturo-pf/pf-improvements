# PF Improvement Artifact Index

Navigation-only catalog for PF improvement coordination and technical records.

The GitHub Issue is the coordination record. The GitHub Project is the only
source for operational status, priority, queue rank, blockers, and progress.
The canonical artifact is the source for technical evidence and decisions.
This index intentionally does not duplicate those fields.

| ID | Slug | GitHub Issue | Canonical artifact |
|---|---|---|---|
| `IMP-006` | `ecosystem-http-error-baseline` | [Issue](https://github.com/mrturo-pf/pf-base/issues/1) | [artifact](improvements/IMP-006-ecosystem-http-error-baseline/recommendation.md) |
| `IMP-007` | `cloud-run-observability-and-capacity` | [Issue](https://github.com/mrturo-pf/pf-base/issues/2) | [artifact](improvements/IMP-007-cloud-run-observability-and-capacity/recommendation.md) |
| `IMP-009` | `scheduler-oidc-hardening` | [Issue](https://github.com/mrturo-pf/pf-base/issues/3) | [artifact](improvements/IMP-009-scheduler-oidc-hardening/recommendation.md) |
| `IMP-010` | `ecosystem-improvement-tracking-migration` | [Issue](https://github.com/mrturo-pf/pf-base/issues/4) | [artifact](improvements/IMP-010-ecosystem-improvement-tracking-migration/recommendation.md) |
| `IMP-001` | `scheduler-credential-exposure-remediation` | [Issue](https://github.com/mrturo-pf/pf-base/issues/5) | [artifact](improvements/IMP-001-scheduler-credential-exposure-remediation/recommendation.md) |
| `IMP-005` | `cloud-deployer-identity-hardening` | [Issue](https://github.com/mrturo-pf/pf-base/issues/6) | [artifact](improvements/IMP-005-cloud-deployer-identity-hardening/recommendation.md) |
| `IMP-003` | `database-runtime-role-hardening` | [Issue](https://github.com/mrturo-pf/pf-base/issues/7) | [artifact](improvements/IMP-003-database-runtime-role-hardening/recommendation.md) |
| `IMP-004` | `pf-rates-database-secret-access-review` | [Issue](https://github.com/mrturo-pf/pf-base/issues/8) | [artifact](improvements/IMP-004-pf-rates-database-secret-access-review/recommendation.md) |
| `IMP-008` | `database-identifier-length-policy` | [Issue](https://github.com/mrturo-pf/pf-base/issues/9) | [artifact](improvements/IMP-008-database-identifier-length-policy/recommendation.md) |
| `IMP-002` | `neon-credential-and-backup-hardening` | [Issue](https://github.com/mrturo-pf/pf-base/issues/10) | [artifact](improvements/IMP-002-neon-credential-and-backup-hardening/recommendation.md) |
| `HIST-007` | `pf-svc-income-renaming` | [Issue](https://github.com/mrturo-pf/pf-base/issues/11) | [artifact](improvements/HIST-007-pf-svc-income-renaming/recommendation.md) |
| `HIST-008` | `gcp-scheduler-credential-exposure` | [Issue](https://github.com/mrturo-pf/pf-base/issues/12) | [artifact](improvements/HIST-008-gcp-scheduler-credential-exposure/investigation.md) |
| `HIST-009` | `employers-contracts-maintenance` | [Issue](https://github.com/mrturo-pf/pf-base/issues/13) | [artifact](improvements/HIST-009-employers-contracts-maintenance/recommendation.md) |
| `HIST-010` | `health-additional-uf-mismatch` | [Issue](https://github.com/mrturo-pf/pf-base/issues/14) | [artifact](improvements/HIST-010-health-additional-uf-mismatch/investigation.md) |
| `HIST-011` | `payroll-operations-endpoint-usage` | [Issue](https://github.com/mrturo-pf/pf-base/issues/15) | [artifact](improvements/HIST-011-payroll-operations-endpoint-usage/investigation.md) |
| `HIST-012` | `cli-removal` | [Issue](https://github.com/mrturo-pf/pf-base/issues/16) | [artifact](improvements/HIST-012-cli-removal/investigation.md) |
| `HIST-013` | `future-increase-ipc-extrapolation` | [Issue](https://github.com/mrturo-pf/pf-base/issues/17) | [artifact](improvements/HIST-013-future-increase-ipc-extrapolation/recommendation.md) |
| `HIST-014` | `net-pay-prediction-reimplementation` | [Issue](https://github.com/mrturo-pf/pf-base/issues/18) | [artifact](improvements/HIST-014-net-pay-prediction-reimplementation/recommendation.md) |
| `HIST-015` | `pay-period-columns-removal` | [Issue](https://github.com/mrturo-pf/pf-base/issues/19) | [artifact](improvements/HIST-015-pay-period-columns-removal/recommendation.md) |
| `HIST-016` | `payroll-update-delete` | [Issue](https://github.com/mrturo-pf/pf-base/issues/20) | [artifact](improvements/HIST-016-payroll-update-delete/recommendation.md) |
| `HIST-017` | `payroll-natural-key-conflict` | [Issue](https://github.com/mrturo-pf/pf-base/issues/21) | [artifact](improvements/HIST-017-payroll-natural-key-conflict/recommendation.md) |
| `HIST-018` | `pdf-import` | [Issue](https://github.com/mrturo-pf/pf-base/issues/22) | [artifact](improvements/HIST-018-pdf-import/recommendation.md) |
| `HIST-019` | `pdf-template-management` | [Issue](https://github.com/mrturo-pf/pf-base/issues/23) | [artifact](improvements/HIST-019-pdf-template-management/recommendation.md) |
| `HIST-020` | `pf-rates-batch-lookup` | [Issue](https://github.com/mrturo-pf/pf-base/issues/24) | [artifact](improvements/HIST-020-pf-rates-batch-lookup/recommendation.md) |
| `HIST-021` | `spreadsheet-export` | [Issue](https://github.com/mrturo-pf/pf-base/issues/25) | [artifact](improvements/HIST-021-spreadsheet-export/recommendation.md) |

## Source-of-truth rules

- Use the linked GitHub Issue for intake, coordination, dependencies, next action, and resolution.
- Use the GitHub Project for current status, categorical priority, numeric queue rank, and operational views.
- Use the canonical Git artifact for investigation findings, design decisions, implementation plans, and release evidence.
- Do not add task state, ownership, repository lists, scope summaries, or duplicate notes to this index.
