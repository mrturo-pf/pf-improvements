# Brief: API endpoint coverage and Postman automation

Date: 2026-10-25
Status: proposed
Level: L
Scope: Build a safe, repeatable validation path that inventories PF HTTP endpoints and executes appropriate Postman requests automatically.
Related artifacts: [investigation](investigation.md) · [recommendation](recommendation.md) · [plan](plan.md)
Related Issue: [#35](https://github.com/mrturo-pf/pf-base/issues/35)
Approved: pending owner decision
Superseded-by: none

## Objective

Ensure that every supported HTTP endpoint has an explicit contract representation
and an automated validation path, reducing missed regressions caused by manual
request-by-request Postman execution.

## Non-objectives

- Replacing service repositories as the source of API implementation or OpenAPI
  truth;
- treating Postman as a general-purpose unit or regression-test replacement;
- running destructive requests against production or GCP by default;
- storing credentials, raw production responses, personal data, payroll data,
  payslips, or health data in GitHub, Postman JSON, or test reports;
- changing public endpoint behavior as part of the automation effort;
- adding always-on infrastructure or a paid test platform before the cheaper CI
  and Newman approach is evaluated.

## Current behavior

The canonical Postman collection contains requests for the ecosystem services and
is synchronized to Postman by GitHub Actions. The workflow validates JSON and
pushes assets, but it does not run the requests or compare the catalog with the
owning services' route definitions. Manual execution can therefore miss requests,
new endpoints, response-shape regressions, and unsafe request ordering.

## Target operating model

| Concern | Target source or mechanism |
|---|---|
| HTTP implementation and route truth | Owning service route definitions and OpenAPI |
| Request catalog and environments | `pf-postman` JSON |
| Endpoint coverage | Automated OpenAPI/route-to-Postman inventory check |
| Safe smoke execution | Newman against LOCAL and approved read-only GCP requests |
| Mutating workflows | Synthetic fixtures, explicit setup/cleanup, isolated environment |
| Destructive workflows | Manual or explicitly authorized workflow dispatch only |
| Results | CLI plus JUnit artifacts, without sensitive payloads |
| Process and release evidence | This improvement's plan and validation record |

## Required outcomes

1. Every supported `pf-rates` and `pf-svc-income` HTTP route has a documented
   Postman representation or an explicit reason for exclusion.
2. The collection has deterministic assertions for status, response type, and
   endpoint-specific contract fields.
3. A Newman smoke job runs safe requests without requiring manual execution.
4. Mutating workflows use deterministic synthetic data and cleanup.
5. Destructive operations are excluded from default CI and require an explicit
   approval/input boundary.
6. CI publishes actionable pass/fail reports without secrets or raw sensitive
   payloads.
7. Collection ordering and request dependencies remain deterministic.
8. The design remains compatible with the one-way repository-to-Postman sync.
9. The cheapest viable implementation uses repository CI and Newman before any
   additional hosted service is considered.

## Acceptance criteria

- A coverage checker reports missing, stale, duplicate, and intentionally excluded
  endpoint mappings.
- A local command can run the safe collection subset and return a non-zero exit
  code on failed assertions or transport failures.
- CI runs the safe subset on relevant collection, environment, service contract,
  and test-runner changes.
- The report identifies service, folder, request, HTTP method, path, status, and
  sanitized failure reason.
- The default workflow cannot delete production records or refresh external data
  providers accidentally.
- API keys are injected only into ephemeral runtime files or environment variables.
- Documentation explains fixture setup, cleanup, dependencies, and rerun behavior.

## Constraints and invariants

- Service API documentation and OpenAPI remain authoritative for implementation.
- Cross-repository changes follow PF ownership boundaries.
- No production mutation is implied by CI access.
- Existing Postman environment files retain empty committed API-key values.
- The automation must support CSV, binary/file, async-job, chained, and JSON
  response types without pretending they share one assertion shape.
- All durable artifacts and reports must be sanitized.
