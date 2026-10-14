# Plan: Cloud Run observability and capacity

Date: 2026-10-12
Status: in progress
Level: M
Scope: Cheapest viable Cloud Run observability, capacity, probe, and database connection-budget baseline for PF services.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md) · [runtime inventory](runtime-inventory.md) · [capacity model](capacity-model.md) · [probe validation](probe-validation.md) · [synthetic validation](synthetic-validation.md) · [operational validation](operational-validation.md)
Approved: 2026-10-13 by owner (conversation)
Superseded-by: none

## 1. Gates

- [x] Initial evidence boundary and cost constraint recorded.
- [x] Brief and recommendation approved.
- [x] Current reusable workflow and service settings inventoried.
- [x] Health/probe semantics validated for both services.
- [x] Database connection budget agreed with `pf-db`.
- [x] Explicit pool limits adopted by both consumers.
- [x] Alert ownership and thresholds approved.
- [x] Representative read-only synthetic validation and Neon correlation passed.
- [x] Revision-overlap routing and restoration validated.
- [ ] Per-service failure/timeout and scale-out validation passed.
- [x] Shared default changes, if any, released with rollback evidence.

## 2. Implementation slices

### Slice 1 — Runtime inventory

Record current Cloud Run settings, workflow inputs, health endpoints, pool sizes,
timeouts, concurrency, max instances, and existing Cloud Monitoring signals.

### Slice 2 — Capacity model

Calculate the connection upper bound for each service and compare it with the
approved PostgreSQL budget, including deployment overlap and operational headroom.
The parametric model is approved by `pf-db` and both consumers now declare the
explicit pool upper bound; probe and runtime validation remain required.

### Slice 3 — Probe and signal validation

Exercise startup, health, dependency failure, timeout, scaling, and representative
request scenarios with synthetic data. Define only actionable alerts.

The contract for dependency failure, timeout, scale-out, overlap, alert ownership,
release, and rollback is approved in [operational validation](operational-validation.md).
Execution evidence remains open.

### Slice 4 — Adoption decision

Apply changes to shared defaults only after both services pass validation. Preserve
scale-to-zero and document rollback for every setting change.

## 3. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-10-14 | in progress | Latest stable-DNS scale run archive `IMP-007-gcp-scale-20261014T012556Z.tar.gz`: pf-rates 2,557/2,560 HTTP 200 and pf-payroll 2,555/2,560; immediate instance metric query returned no timeSeries, so next step is delayed 30-minute metric check for pf-rates. | [operational validation](operational-validation.md); `scripts/cloudshell/IMP-007-gcp-instance-metric-check.sh` |

## 4. Release record

- Commits: published; latest `pf-improvements` IMP-007 documentation commit `3a36ea9`
- Workflow runs: production deploy/migration workflows passed
- Owner approval: recorded 2026-10-13; production gates approved 2026-10-13
- Service validation: representative and rollback validation passed; pf-rates scale-out conclusion pending delayed metric query
- Rollback evidence: passed controlled Cloud Shell health rollback; current revisions restored at 100%
