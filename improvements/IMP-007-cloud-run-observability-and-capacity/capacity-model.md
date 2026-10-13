# IMP-007 capacity model

Date: 2026-10-13
Status: approved
Scope: Approved connection-budget model for `pf-rates`, `pf-payroll`, and the `pf-db` migration job.
Evidence boundary: sanitized repository evidence and explicit scenarios only. No production database inspection or mutation.

## 1. Model

The release gate uses this upper-bound model per service:

```text
service_connections = max_instances × connections_per_instance
release_connections = service_connections × revision_overlap_factor
fleet_connections = sum(release_connections) + migration_job_connections + headroom
```

Where:

- `max_instances` is the Cloud Run service maximum;
- `connections_per_instance` is the explicitly approved pool upper bound;
- `revision_overlap_factor` represents old and new revisions holding connections
  during rollout;
- `migration_job_connections` covers the on-demand `pf-db` migration job;
- `headroom` is reserved capacity for operational safety and must not be silently
  consumed by application pools.

The original planning formula remains useful for a single revision:

```text
max_instances × pool_size × connection_factor
```

This artifact extends it so deployment overlap and the migration job are visible
rather than hidden in an unexplained factor.

## 2. Known inputs

| Input | Current evidence | Status |
|---|---:|---|
| `pf-rates` max instances | `2` | confirmed in shared workflow |
| `pf-payroll` max instances | `2` | confirmed in shared workflow |
| Revision overlap | unknown | requires `pf-db`/operations decision |
| Service pool upper bounds | implicit | must become explicit before release |
| Migration job connections | unknown | requires `pf-db` confirmation |
| PostgreSQL connection budget | not documented locally | blocking approval input |
| Headroom percentage/quantity | unknown | requires owner decision |

## 3. Sensitivity scenarios

The following scenarios are planning arithmetic, not approved configuration. They
show the impact of making pool limits explicit for the current `max_instances=2`.

| Pool upper bound per instance | One service, one revision | One service, two revisions | Both services, two revisions each |
|---:|---:|---:|---:|
| `5` | `10` | `20` | `40` |
| `10` | `20` | `40` | `80` |
| `15` | `30` | `60` | `120` |

These values exclude the migration job and headroom. If a pool uses a base size
plus overflow, the model must use the sum of both as the upper bound; using only
`pool_size` would understate capacity.

## 4. Neon provider evidence

The `pf-db` owners supplied Neon evidence on 2026-10-13 reporting:

```text
max_connections=901
active_connections=12
```

The active-session snapshot is approximately `1.33%` of the provider ceiling and
uses `12` of the approved PF reservation of `80`, leaving `68` reserved PF
connections unused at observation time. This is a point-in-time observation, not
a traffic trend; it does not justify increasing pools or Cloud Run limits.

## 5. `pf-db` coordination result

The `pf-db` owners approved the connection budget on 2026-10-13. The durable
policy is recorded in [`pf-db/docs/connection-budget.md`](https://github.com/mrturo-pf/pf-db/blob/main/docs/connection-budget.md).

Approved values:

- total PF budget: `80` connections;
- `pool_size=5`, `max_overflow=0` per service instance;
- `max_instances=2` per service;
- rollout overlap factor: `2` revisions;
- migration reservation: `5`;
- operator reservation: `5`;
- operational headroom: `20`;
- calculated rollout usage: `70`, leaving `10` connections of margin.

The approval applies to the capacity model. It does not silently change service
code or Cloud Run settings; consumer adoption and validation remain required.

## 6. Required decisions from `pf-db`

No further budget decision is required for the current model. Consumer adoption
must still provide evidence that the explicit pool configuration is in effect.

No value is inferred from a provider default, local Docker configuration, or a
connection string. The model is intentionally conservative until those decisions
are recorded.

## 7. Proposed acceptance check

For each service and release:

```text
fleet_connections <= approved_postgresql_budget - approved_headroom
```

The check must use explicit pool limits and include the migration-job reservation.
A release that cannot calculate this value is blocked; it must not silently fall
back to library defaults.

## 8. Current result

Slice 2 is approved and the explicit pool contract is adopted by both consumers.
The model uses `70` of the approved `80` connections during conservative
two-revision rollout conditions, leaving `10` connections of margin. Probe,
concurrency, timeout, and synthetic evidence remain open. No Cloud Run setting
was changed.
