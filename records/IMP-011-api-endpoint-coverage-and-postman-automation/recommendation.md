# Recommendation: API endpoint coverage and Postman automation

Date: 2026-10-25
Status: released
Level: L
Scope: Automated endpoint inventory, Postman assertions, Newman execution, and safe CI orchestration for the PF HTTP surfaces.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [plan](plan.md)
Related Issue: [#35](https://github.com/mrturo-pf/pf-base/issues/35)
Approved: 2026-10-28 by a0a11b7 (explicit authorization)
Superseded-by: none

## 1. Recommendation

Adopt a layered automation model rather than a single blind collection run:

1. compare service OpenAPI/route definitions with Postman requests;
2. add common and endpoint-specific Postman assertions;
3. execute a safe Newman smoke subset automatically;
4. execute mutating workflows only with isolated synthetic fixtures;
5. keep destructive and provider-refresh operations behind explicit workflow
   inputs and a separate safety boundary.

The first implementation should live primarily in `pf-postman`, with small
contract-export or inventory adapters in service repositories only where needed.

## 2. Coverage contract

The coverage checker should normalize and compare:

- service identifier;
- HTTP method;
- route path with path-parameter placeholders;
- intentional exclusions and their documented reason.

It must report missing Postman requests, stale Postman paths, duplicates, and
unmapped operations. It should consume OpenAPI or route metadata from the owning
service rather than parse implementation details in `pf-postman`.

`pf-sheets` Web App endpoints require a separate sanitized route inventory because
that runtime does not expose the same FastAPI OpenAPI surface.

## 3. Execution tiers

### Tier 1: smoke

Run on LOCAL and, after explicit approval of the target, on GCP:

- health checks;
- safe reads and list queries;
- deterministic exports that do not create unbounded jobs;
- response content-type and schema checks.

### Tier 2: integration workflows

Run against LOCAL or an isolated test database with setup and cleanup:

- imports;
- employer and contract maintenance;
- template lifecycle;
- chained preview/import flows;
- asynchronous export lifecycle.

### Tier 3: destructive or external-provider operations

Do not run by default. Require explicit workflow dispatch, a clearly identified
non-production target, synthetic identifiers, cleanup evidence, and bounded rate
and timeout settings.

## 4. Assertion standard

Every executable request should have, as applicable:

- transport success or an intentionally documented status;
- bounded response time;
- expected content type;
- valid JSON, CSV, or binary response handling;
- endpoint-specific required fields and invariants;
- correlation between setup, request, and cleanup identifiers without recording
  sensitive payloads.

Generic assertions must not replace domain assertions, and endpoint-specific
assertions must not be copied into unrelated requests.

## 5. CI design

Add a `run-postman-tests` workflow with:

- Newman installed in the runner;
- ephemeral environment materialization from GitHub Secrets;
- safe smoke execution on relevant pull requests or controlled pushes;
- JUnit and CLI reports with sanitized failure summaries;
- `--bail` or equivalent failure propagation;
- separate manual execution for destructive tiers.

The existing sync workflow remains one-way asset publication. Test execution must
not mutate committed collection/environment JSON or send real secrets to reports.

## 6. Alternatives considered

- **Manual Postman execution:** rejected because it does not prove coverage and
  is easy to omit after endpoint changes.
- **Blind Newman execution of every request:** rejected because the collection has
  mutations, deletes, provider refreshes, async jobs, file dependencies, and
  request ordering constraints.
- **Only service unit tests:** rejected because they do not validate the shared
  Postman catalog, deployed URLs, authentication wiring, or cross-service request
  contract.
- **Paid external test platform:** deferred because CI plus Newman and existing
  repository tooling are the cheapest viable first implementation.

## 7. Decision gate

Approve the layered model, the coverage comparison contract, the tier boundaries,
and the secret/reporting rules. Do not enable GCP or destructive execution until
fixture ownership, cleanup, target selection, and explicit authorization are
validated.
