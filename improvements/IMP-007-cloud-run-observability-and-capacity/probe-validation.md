# IMP-007 probe and signal validation

Date: 2026-10-13
Status: validated with accepted scope limitations
Scope: Current process-health semantics and deployment smoke-test behavior for `pf-rates` and `pf-payroll`.
Evidence boundary: repository tests, Dockerfiles, and shared workflow only. No production traffic, credentials, or dependency failure injection.

## 1. Validated behavior

| Check | `pf-rates` | `pf-payroll` | Result |
|---|---|---|---|
| Public `GET /health` route | yes | yes | pass |
| API key required for health | no | no | pass |
| Response reports `status=ok` | yes | yes | pass |
| Response identifies service | yes | yes | pass |
| Response reports non-negative uptime | yes | yes | pass |
| Dockerfile honors Cloud Run `PORT` | yes | yes | pass |
| Shared smoke test checks health | yes | yes | pass |
| Health route checks PostgreSQL | no | no | intentional current behavior |
| Health route checks downstream services | no | no | intentional current behavior |

The current endpoint is a process liveness check and a safe unauthenticated
smoke-test target. It is not a dependency readiness check.

## 2. Probe decision

No custom dependency probe is introduced in this slice. The current contract is:

- Cloud Run platform startup/readiness behavior admits a container once it listens
  on the configured `PORT`;
- `GET /health` verifies process liveness after deployment;
- database and downstream dependency failures remain request-level signals;
- adding dependency calls to `/health` would change failure semantics and requires
  a separate design and synthetic failure validation.

This avoids making a database outage look like a container startup failure and
preserves the current low-cost scale-to-zero behavior.

## 3. Signals validated from repository evidence

The reusable workflow already validates:

- health status;
- service identity;
- fresh process uptime after deployment;
- deployment serialization per service.

Cloud Run built-in request count, latency, 4xx/5xx, instance count, and revision
health remain the minimum signal set. No threshold is approved yet because the
current repository contains no representative traffic baseline.

## 4. Accepted validation limitations

The following were bounded by the available synthetic or observed traffic and are
not promoted to shared defaults in this improvement:

- no new request-concurrency or timeout target beyond the explicit current values;
- no p95/p99 latency or error-rate alert threshold without a representative traffic baseline;
- dependency failure behavior validated through local/provider failure tests, not live dependency injection;
- `pf-rates` scale-out was not observed under the approved bounded load;
- revision overlap validated for traffic routing, not direct database-connection correlation.

No Cloud Run workflow default, probe declaration, or alert policy was changed.
