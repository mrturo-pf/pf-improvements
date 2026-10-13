# IMP-007 synthetic validation

Date: 2026-10-13
Status: partially validated; remaining scenarios open
Scope: Local synthetic validation of health burst, startup, timeout, and representative request behavior.

## Attempted validation

The supported project command was attempted for both consumers:

```text
uv run --extra dev pytest ...
```

The environment could not resolve dependencies because `uv` attempted to reach
public PyPI and failed with a corporate certificate error:

```text
invalid peer certificate: UnknownIssuer
```

No production endpoint, database, credential, or Cloud Run resource was used.

## 2. Completed synthetic checks

After clearing proxy variables and using the approved corporate package index, both
service environments were restored and the focused checks passed:

```text
pf-rates health/auth tests:   2 passed
pf-payroll health/auth tests: 4 passed
pf-rates health burst:        50/50 passed
pf-payroll health burst:      50/50 passed
```

The burst used an in-process ASGI transport and synthetic requests only. It verifies
that the public process-health route remains responsive under 50 concurrent
requests; it does not exercise PostgreSQL or business endpoints.

## 3. Cloud Run observations

Read-only inspection of the live services confirmed the effective settings:

```text
containerConcurrency: 80
request timeout:       300s
maxScale:              2
container port:        8080
```

Health requests also produced this limited evidence:

```text
pf-rates:   first request ~10.5s; subsequent requests ~0.85–0.90s; HTTP 200
pf-payroll: first request exceeded a 15s client limit; subsequent requests ~0.86–0.91s; HTTP 200
```

These results demonstrate cold-start sensitivity but do not establish a business
request SLO. They support preserving the current 300-second timeout while more
representative scenarios are tested.

A read-only Cloud Logging query was blocked by the organization's VPC Service
Controls policy, so startup log evidence is unavailable from this environment.

## 4. Neon-correlated representative validation

A local execution outside the restricted network completed on 2026-10-13 using
the Neon read-only runner. The HTTP load and `pg_stat_activity` sampler ran during
the same execution:

```text
pf-payroll: 181/181 HTTP 200
pf-rates:   153/153 HTTP 200
Neon activity rows: 144
Maximum observed total connections: 7
Approved PF connection budget: 80
```

Observed read-only latency summaries:

```text
pf-payroll: p50 297.624 ms; p95 529.395 ms; p99 776.370 ms
pf-rates:   p50 389.821 ms; p95 437.388 ms; p99 472.859 ms
```

The run produced no HTTP failures and stayed well below the approved connection
budget. This validates the representative read-only path and simultaneous Neon
sampling. It does not prove scale-out, two-revision overlap, dependency failure,
or timeout behavior.

## 6. GCP Cloud Run observation

A read-only Cloud Shell archive was collected on 2026-10-13 for project
`coreassistant-474022` in `us-central1`. It confirmed:

```text
pf-rates:
  concurrency: 80
  timeout: 300s
  maxScale: 2
  traffic: 100% latest ready revision
  latest revision: pf-rates-00060-krl
  ready deployment duration: 10.98s

pf-payroll:
  concurrency: 80
  timeout: 300s
  maxScale: 2
  traffic: 100% latest ready revision
  latest revision: pf-payroll-00062-t6q
  ready deployment duration: 16.72s
```

The archive contained only sanitized service/revision metadata and explicitly
recorded no mutations or secrets. Historical revisions were ready and retired as
expected. This confirms the effective production baseline and readiness durations,
but does not prove simultaneous old/new revision connection overlap during a live
deployment.

## 7. Current evidence

The following repository-level checks remain valid:

- both services expose a public `/health` route;
- the shared workflow smoke test validates health status, service identity, and
  fresh process uptime;
- both consumers declare `pool_size=5` and `max_overflow=0`;
- the approved connection model leaves ten connections of margin under the
  conservative two-revision rollout assumption.

These checks do not substitute for synthetic concurrency, timeout, cold-start,
or representative request validation.

## 8. Gate decision

The health-burst portion is complete. The per-service synthetic validation gate
remains **open** for startup/cold-start, representative request, dependency
failure, timeout, scale-out, and two-revision connection checks. Do not change
shared Cloud Run concurrency, timeout, probe, or alert defaults until those
scenarios pass with the approved corporate test environment.
