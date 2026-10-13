# Investigation: Cloud Run observability and capacity

Date: 2026-10-12
Status: investigating
Level: M
Scope: Establish the cheapest viable Cloud Run observability, probe, scaling, concurrency, and database connection-budget baseline for PF services.
Owner: `pf-common`
Related artifacts: [brief](brief.md) · [recommendation](recommendation.md) · [plan](plan.md) · [runtime inventory](runtime-inventory.md) · [capacity model](capacity-model.md) · [probe validation](probe-validation.md) · [synthetic validation](synthetic-validation.md) · [register](../../index.md)
Superseded-by: none

## 1. Question

What minimum Cloud Run operational baseline protects `pf-rates` and `pf-payroll`
from silent availability, capacity, and database-connection failures without
introducing unnecessary paid infrastructure?

## 2. Evidence boundary

The baseline must cover the shared reusable deployment workflow and its consumers:

- health/readiness behavior and probe semantics;
- min/max instances, concurrency, CPU/memory, timeout, and scale-to-zero;
- Cloud Run request/error/latency signals;
- database connection pool sizing against the shared PostgreSQL budget;
- rollback and release evidence.

The investigation must use sanitized metadata and synthetic load. It must not record
credentials, raw request payloads, personal/financial data, or database contents.

## 3. Initial findings and questions

- The ecosystem favors `min-instances=0`, bounded max instances, and free existing
  tooling before paid monitoring.
- A service-level max-instance setting is not sufficient unless the aggregate
  database connection budget is explicit.
- Health checks must distinguish process readiness from dependency availability;
  otherwise deployments can either admit broken revisions or block unnecessarily.
- Alerts should begin with existing Cloud Run/Cloud Monitoring signals and only add
  custom metrics when a concrete gap is demonstrated.

Open questions:

1. Which health endpoint is suitable for startup/readiness versus liveness?
2. Which latency/error thresholds are meaningful for the current traffic profile?
3. Which alerts are actionable enough to justify operational ownership?

## 4. Slice 1 result

The local runtime inventory is complete. It confirms the shared deployment values
(`min=0`, `max=2`, `1 CPU`, `512Mi`, port `8080`) and identifies the remaining
control gaps: request concurrency, timeout, probe declarations, and explicit pool
limits. Both `/health` routes are process-only checks. The detailed evidence is in
[runtime-inventory.md](runtime-inventory.md).

The next blocking question is the PostgreSQL connection budget and rollout overlap
policy owned by `pf-db`; no numeric budget is assumed from undocumented defaults.
The parametric capacity model is drafted in [capacity-model.md](capacity-model.md).

## 5. Current conclusion

Create a shared operational baseline and validate it per service before changing
workflow defaults. Do not provision always-on capacity or paid dashboards merely to
close this investigation.
