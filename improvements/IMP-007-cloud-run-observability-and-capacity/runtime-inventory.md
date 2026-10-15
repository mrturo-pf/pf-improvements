# IMP-007 runtime inventory

Date: 2026-10-13
Status: inventory complete (local repository evidence)
Scope: Slice 1 inventory for the shared Cloud Run workflow and its current Python consumers.
Evidence boundary: repository configuration only; no credentials, production payloads, database contents, or live Cloud Run mutation.

## 1. Shared deployment workflow

Source: `pf-common/.github/workflows/deploy-reusable.yml` at the inspected `main` checkout.

| Setting | Current value | Evidence / interpretation |
|---|---:|---|
| Region | `us-central1` | Workflow environment |
| Minimum instances | `0` | Scale-to-zero invariant |
| Maximum instances | `2` | Explicit `gcloud run deploy` argument |
| CPU | `1` | Explicit deploy argument |
| Memory | `512Mi` | Explicit deploy argument |
| Container port | `8080` | Explicit deploy argument; Cloud Run injects `PORT` |
| Request concurrency | `80` | Explicit deploy argument; matches live service configuration |
| Request timeout | `300s` | Explicit deploy argument; matches live service configuration |
| Deployment approval | enabled by both callers | `require_approval: true` |
| Deployment serialization | per service | Workflow `concurrency` group; `cancel-in-progress: false` |
| Observability source | built-in Cloud Run signals first | No custom metric or paid monitoring provisioned |

The workflow now makes request concurrency and timeout explicit to preserve the
live service contract. It still does not set Cloud Run startup, readiness, or
liveness probes explicitly; those remain application/platform behavior and require
a separate decision before being treated as a controlled baseline.

## 2. Service comparison

| Service | App port in local Makefile | Workflow port | Health route | Health dependencies | Database pool configuration |
|---|---:|---:|---|---|---|
| `pf-rates` | `8001` | `8080` | `GET /health` | process-only response | `pool_size=5`, `max_overflow=0`, `pool_pre_ping=true`, `pool_recycle=300` |
| `pf-payroll` | `8000` | `8080` | `GET /health` | process-only response | `pool_size=5`, `max_overflow=0`, `pool_pre_ping=true`, `pool_recycle=300` |

The local port differences are not necessarily a production defect because the
container command and Cloud Run `PORT` contract can differ from local development.
They are nevertheless documentation drift: service deployment docs should describe
the shared workflow's effective production port rather than imply that local ports
are deployed unchanged.

Both health routes return `status`, service name, and process uptime without probing
PostgreSQL or downstream services. This is suitable evidence for process liveness
and the current smoke test, but it is not evidence that dependencies are ready.
No readiness or startup probe is declared in the reusable workflow or service
Dockerfiles.

## 3. Connection-budget baseline

The approved `pf-db` policy is documented at
[pf-db/docs/connection-budget.md](https://github.com/mrturo-pf/pf-db/blob/main/docs/connection-budget.md).
It sets a total budget of `80` connections, with `pool_size=5` and
`max_overflow=0` per service instance. Under two revisions, two instances, two
services, five connections per instance, five migration connections, five
operator connections, and twenty headroom connections, modeled usage is `70`,
leaving a margin of `10`.

Consumer services have now adopted the explicit pool limits in their database
session factories. The focused unit tests assert the upper bound and stale
connection protection. No runtime or deployment setting was changed.

The inspected Neon provider reports `max_connections=901` and the supplied
`pg_stat_activity` snapshot reports `active_connections=12` (`1.33%` of the
provider ceiling). The snapshot uses `12` of the PF reservation of `80`, leaving
`68` reserved PF connections unused at that observation time. It is not a traffic
trend; the application reservation remains `80` until sustained evidence and
other-consumer reservations justify a review.

## 4. Findings and follow-ups

1. **Confirmed:** scale-to-zero and bounded `max=2` are shared deployment behavior.
2. **Confirmed:** deployment serialization prevents overlapping workflow runs per
   service, but it does not prove that old and new Cloud Run revisions cannot both
   hold connections during rollout.
3. **Confirmed:** smoke testing checks process health only.
4. **Accepted limitation:** startup/readiness/liveness semantics, representative
   timeout behavior, and alert thresholds are not expanded in this improvement;
   concurrency and timeout are explicit in the shared workflow.
5. **Documentation note:** local development ports (`8000`/`8001`) differ from
   the shared production port `8080`; deployment docs now describe both contexts.
6. **Follow-up evidence:** active-session usage from `pg_stat_activity`, broader
   timeout behavior, and alert thresholds may be revisited if traffic or service
   behavior changes; they are not blockers for the closed baseline.

No application, workflow, Cloud Run, IAM, database, or alert configuration was
changed by this inventory.
