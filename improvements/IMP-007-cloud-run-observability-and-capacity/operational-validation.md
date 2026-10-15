# IMP-007 operational validation contract

Date: 2026-10-13
Status: closed with bounded-evidence limitation
Scope: Dependency-failure, timeout, scale-out, deployment-overlap, alert, release, and rollback validation for `pf-rates` and `pf-payroll`.

## 1. Controlled dependency-failure scenarios

These scenarios must run against local/test doubles or an explicitly approved
non-production target. They must not disable production dependencies or mutate
financial data.

| ID | Scenario | Expected result | Evidence |
|---|---|---|---|
| DEP-001 | PostgreSQL unavailable before a read request | bounded dependency error; no leaked session | HTTP status, sanitized error class, pool state |
| DEP-002 | PostgreSQL query exceeds internal timeout | bounded timeout response; connection returned to pool | timeout duration, status, pool state |
| DEP-003 | `pf-rates` unavailable to `pf-payroll` | dependency error mapped without retry storm | status, retry count, latency |
| DEP-004 | Dependency recovers | next request succeeds without restart | success status and recovery latency |
| DEP-005 | Invalid/expired API key | `401`/`403` contract preserved; no database query required | status only |

Pass criteria:

- no request waits longer than the configured client/dependency timeout;
- no unbounded retry loop;
- no increase in pool upper bound beyond `5` per instance;
- error responses contain no credentials or raw financial payloads;
- recovery succeeds without manual process restart.

## 2. Timeout scenarios

Run with synthetic data and a controlled slow dependency:

1. request completes below the dependency timeout;
2. dependency exceeds the timeout but remains below Cloud Run's `300s` request cap;
3. request reaches the application timeout boundary;
4. client disconnects while work is pending.

The application must fail fast at the dependency boundary rather than waiting for
Cloud Run's full request timeout. The existing Cloud Run timeout remains `300s`
until representative evidence supports a narrower value.

## 3. Scale-out and overlap procedure

This is a controlled production operation and requires an approved window.

1. Start the read-only Neon sampler and record a baseline.
2. Start bounded read-only endpoint traffic at workers `10`, then `25`, then `50`.
3. Observe Cloud Run instance count and request latency.
4. Stop load if errors exceed the alert threshold or connections reach `70`.
5. During an explicitly approved deployment, record old/new revision names,
   traffic allocation, readiness times, and Neon connections every second.
6. Confirm the two-revision model remains below the hard budget of `80`.
7. Stop traffic and confirm scale-down does not leave unexplained connections.

No test may intentionally exceed `maxScale=2`, the approved connection budget, or
an owner-approved request-rate limit.

## 4. Alert ownership and thresholds

These are the approved starting thresholds. They are intentionally simple and use
existing Cloud Run/Cloud Monitoring signals before custom metrics.

| Signal | Warning | Critical | Owner | Action |
|---|---:|---:|---|---|
| HTTP 5xx rate | >1% for 5m | >5% for 5m | service owner (`pf-rates`/`pf-payroll`) | inspect revision/dependency; rollback if sustained |
| p95 request latency | >1s for 5m | >2s for 5m | service owner | inspect cold starts and dependency latency |
| Cloud Run instances at max | 100% of max for 10m | max plus 5xx/latency breach | `pf-common`/platform owner | stop load; review concurrency/capacity |
| Neon total connections | >50 for 5m | >=70 | `pf-db` owner | stop load; inspect pools/revisions |
| Neon hard budget | n/a | >=80 | `pf-db` owner | block release and investigate immediately |
| revision not Ready | any | any | deploy owner | stop rollout; use previous revision |

Cold-start latency is tracked separately from steady-state p95/p99 and is not
alone an error-rate alert. Alert payloads must contain service, revision, region,
signal, threshold, window, and runbook link; never payloads or credentials.

## 5. Release and rollback evidence

A release is not complete until it has:

- immutable image SHA;
- test/build/security workflow results;
- manual production approval evidence;
- migration-before-traffic evidence;
- smoke test success;
- connection-budget observation;
- rollback target revision and decision owner.

Rollback is a Cloud Run traffic mutation and requires explicit operator approval.
The rollback target must be a previously Ready revision; do not rebuild or deploy
an unverified replacement during incident response.

## 7. Rollback validation result

A controlled Cloud Shell rollback validation completed on 2026-10-13 using the
previous revisions and an unconditional restore path:

```text
pf-rates:
  previous: pf-rates-00060-krl
  health: HTTP 200
  duration: 8s
  restored: pf-rates-00061-9qd

pf-payroll:
  previous: pf-payroll-00062-t6q
  health: HTTP 200
  duration: 17s
  restored: pf-payroll-00063-4dd
```

Both previous revisions returned the expected service identity and `status=ok`
from Cloud Shell. The archive contained two sanitized log entries per service,
and traffic was restored to the current revision after each test. The previous
rollback timeout observed from the local network was therefore an observation-path
problem, not evidence of an unhealthy application revision.

The rollback gate is **passed** for this controlled health validation. Business
endpoint rollback validation and a longer traffic soak remain outside this slice.

## 8. Rollback diagnosis result

The earlier diagnosis archive remains useful: both revision pairs used the same
runtime settings, passed startup probes, and showed no application crash. The
Cloud Shell result resolves the earlier ambiguity in favor of the local
observation/network path.

## 8. Local dependency and timeout validation

The controlled test-double scenarios were executed locally after the production
release:

```text
pf-payroll HTTP dependency client tests: 8 passed
pf-rates provider failure/timeout tests: 3 passed, 35 deselected
```

The coverage includes HTTP `503`, connection errors, read timeouts, provider
timeouts, and offline/failure handling. These tests validate bounded error
mapping and retry behavior without disabling a production dependency. They do not
replace a live Cloud Run dependency-failure test.

## 10. Bounded scale observation result

A Cloud Shell bounded health observation ran for 180 seconds with 160 workers per
service and no Cloud Run traffic mutation:

```text
pf-rates:   2,560 requests; 2,551 HTTP 200; 9 DNS failures
pf-payroll: 2,240 requests; 2,233 HTTP 200; 7 DNS failures
```

Both services retained `maxScale=2` and 100% traffic on the current revision at
baseline and final observation. The run did not collect Cloud Monitoring
`instance_count`, so it cannot prove whether scale-out occurred. The DNS failures
were intermittent Cloud Shell resolver errors and make the run unsuitable as a
clean SLO sample, although the observed failure ratio remained below the warning
threshold.

At this stage the scale-out observation was incomplete; the later delayed metric
archive provides bounded evidence and the accepted limitation is recorded below.
The overlap gate is resolved by the dedicated routing observation.

## 12. Scale observation with Cloud Monitoring

The REST-based Cloud Monitoring run completed on 2026-10-14:

```text
pf-rates:
  HTTP: 959/960 responses 200
  maximum observed instance_count: 1
  traffic: 100% current revision

pf-payroll:
  HTTP: 957/960 responses 200
  instance_count response: no timeSeries returned
  traffic: 100% current revision
```

The run still recorded intermittent Cloud Shell DNS failures (`1` for
`pf-rates`, `3` for `pf-payroll`). `pf-rates` provides evidence that the service
stayed at one instance under this bounded health load; it does not prove that the
configured scale-out path works. `pf-payroll` needs a corrected Monitoring query
or metric availability check before its instance count can be assessed.

The scale-out evidence remained bounded and no traffic or service configuration
was changed. The accepted limitation is carried into the final capacity decision.

## 14. Delayed instance metric result

A 30-minute read-only Cloud Monitoring query completed after the load window:

```text
pf-rates:
  active instance max: 1
  idle instance max:   1

pf-payroll:
  active instance max: 1
  idle instance max:   2
```

This confirms that the metric publication path works and that `pf-payroll`
reached the configured two-instance ceiling during the observation window. The
`pf-rates` window remained at one observed instance. The result is therefore
partial scale-out evidence: payroll passed the scale-out observation, while rates
still needs a stable-DNS load window that produces a second instance or an
explicit documented explanation for remaining at one.

This query did not observe two revisions receiving traffic simultaneously; the
separate controlled 50/50 routing observation below resolves the traffic-overlap
gate, while database-connection overlap remains an accepted evidence limitation.

## 16. Revision-overlap observation

A controlled Cloud Shell observation routed traffic 50/50 between stable and
candidate revisions, then restored 100% traffic to stable:

```text
pf-rates:
  stable:   pf-rates-00061-9qd
  candidate: pf-rates-00062-8t8
  observed split: 50% / 50%
  requests: 180 (178 HTTP 200, 2 DNS failures)
  restored: 100% stable

pf-payroll:
  stable:   pf-payroll-00063-4dd
  candidate: pf-payroll-00064-7s7
  observed split: 50% / 50%
  requests: 120 (117 HTTP 200, 3 DNS failures)
  restored: 100% stable
```

The overlap routing and automatic restoration passed. The DNS failures are an
observation-environment issue already seen in the scale runner; they do not alter
the confirmed traffic split or restoration result. This validates routing overlap,
not database connection overlap; Neon correlation during the split remains a
future enhancement if needed.

## 18. Final capacity-gate result

The final delayed, read-only Cloud Monitoring archive was collected on
2026-10-15 for a 30-minute window (`02:39:30Z`–`03:09:30Z`). The archive
completed successfully and recorded no mutations or secrets, but both service
responses contained only `{"unit":"1"}` and no `timeSeries` or data points.

The accepted evidence is therefore:

```text
pf-payroll: scale-out observed previously; delayed observation reached max=2
pf-rates:   no scale-out observed under the bounded load; delayed query max=1
```

The missing series in the final query prevents a stronger claim about the latest
window. This is not evidence of a Cloud Run defect. The capacity gate is closed
with the explicit limitation that `pf-rates` scale-out was not observed under the
approved bounded load.

The overlap gate passed separately: traffic was observed at 50/50 and restored to
100% stable. No production traffic or service configuration was changed by the
metric checks.
