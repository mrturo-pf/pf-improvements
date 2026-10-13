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
- [ ] Per-service failure/timeout, scale-out, and overlap validation passed.
- [ ] Shared default changes, if any, released with rollback evidence.

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
| 2026-10-13 | in progress | Production releases and Neon migration completed successfully; authorized rollback observation timed out on both previous revisions after 120s, then traffic was restored to current revisions at 100%. IMP-007 remains open pending diagnosis and a successful controlled rollback. | [operational validation](operational-validation.md); runs `38480997414`, `38481006067`, `38481010085` |

## 4. Release record

- Commits: local commits prepared; see change log
- Workflow runs: pending push and GitHub Actions access
- Owner approval: recorded 2026-10-13
- Service validation: pending
- Rollback evidence: failed previous-revision health checks; current revisions restored at 100%; diagnosis pending
