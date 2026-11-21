# Plan: migrate `pf-rates` to `pf-svc-reference`

Date: 2026-11-20  
Status: approved for execution
Level: L  
Scope: Cross-repository service identity, GCP, consumers, Postman, and `RAT_* → REF_*` schema migration.
Related artifacts: [brief](brief.md) · [investigation](investigation.md) · [recommendation](recommendation.md)
Approved: 2026-11-20 by `mrturo`; execution authorized
Superseded-by: none

## 1. Gates

- [x] Confirm canonical identity `pf-svc-reference`.
- [x] Confirm API key target `PF_REFERENCE_API_KEY`.
- [x] Resolve database-secret contract: use separate `PF_REFERENCE_DATABASE_URL`.
- [x] Approve final `RAT_* → REF_*` object map.
- [ ] Inventory every consumer and active reference before mutation.
- [ ] Inventory GCP resources, IAM, secrets, revisions, and image digests read-only.
- [x] Approve code/package, schema, Postman, GCP, consumer, commit, push, and deploy scopes.
- [ ] Prepare and validate reversible `pf-db` migration locally.
- [ ] Prepare backup/restore and pre-migration schema/count snapshot.
- [ ] Prepare parallel GCP resources with least privilege and scale-to-zero.
- [ ] Update service, workflow, Postman, root, shared-tooling, and consumer identity references.
- [ ] Validate all affected repositories and generated artifacts.
- [ ] Execute migration in a bounded maintenance window with drain/abort evidence.
- [ ] Deploy immutable `pf-svc-reference` revision and validate readiness.
- [ ] Run read-only and authenticated synthetic smoke tests.
- [ ] Execute Go/No-Go and move consumers/traffic atomically.
- [ ] Observe full rollback window and representative financial-data flow.
- [ ] Remove legacy resources only after explicit cleanup approval.
- [ ] Classify retained Cloud Asset Inventory history and close the improvement.

## 2. Required execution order

### Phase 1 — Evidence and design

1. Inspect current `pf-rates` code, OpenAPI, Postman, `pf-svc-income`, `pf-sheets`,
   `pf-common`, `pf-db`, workflows, GCP, and all active consumers.
2. Confirm the full `RAT_*` dependency graph and exact target map.
3. Decide whether `rates` remains an internal package in phase one.
4. Record cost, compatibility, secret, IAM, rollback, and migration decisions.

### Phase 2 — Local implementation

1. Add a hand-written reversible migration for the approved `REF_*` map.
2. Update ORM/models, repository SQL, seeds, tests, docs, grants, indexes, and
   generated references in `pf-rates` and `pf-db`.
3. Update shared workflow/deployment inputs and Postman environments without placing
   secret values in Git.
4. Run local migration upgrade/downgrade, schema/catalog checks, row-count checks,
   aggregate checks, API tests, and full repository quality gates.

### Phase 3 — Parallel deployment

1. Create `pf-svc-reference` Artifact Registry, runtime/deployer accounts,
   Cloud Run service, and API-key secret only after approval.
2. Build/push immutable digest and deploy at scale-to-zero.
3. Validate dependency URL, secret references, IAM, `/health`, and protected routes.
4. Do not move traffic until schema and consumer evidence passes.

### Phase 4 — Controlled migration and cutover

1. Take sanitized backup metadata and pre-migration schema/count snapshot.
2. Enter the approved maintenance window; drain or isolate active traffic.
3. Apply reversible `RAT_* → REF_*` migration.
4. Validate catalog, FK/index/constraint names, row counts, aggregates, grants, and
   service ORM/API compatibility.
5. Run Go/No-Go, update consumers/Postman, and move traffic to the new service.
6. Record revision, digest, workflow IDs, smoke results, and rollback owner.

### Phase 5 — Observation and cleanup

1. Retain old service/image/account/secrets for the full approved window.
2. Observe representative exchange-rate, economic-index, tax-bracket, and export flows.
3. Freeze incompatible schema changes during rollback.
4. Obtain explicit cleanup approval.
5. Disable/destroy legacy API-key versions, delete old resources, and verify active
   inventories contain no old identity names.
6. Classify provider-retained audit history rather than claiming it was deleted.

## 3. Safety and quality rules

- Never read or print secret values into logs, Git, Postman JSON, or generated files.
- Never perform a blind global replacement of `rates`, `payroll`, or financial routes.
- Preserve public API paths unless a separate contract decision changes them.
- Keep files below 600 lines; split cohesive artifacts only when needed.
- Run `pf-db`, `pf-rates`, `pf-svc-income`, `pf-common`, and Postman checks as applicable.
- Do not close the rollback window early without a written owner waiver and explicit
  acceptance of every missing evidence item.

## 4. Change log

| Date | Status | Change | Evidence |
|---|---|---|---|
| 2026-11-20 | approved | Owner confirmed `pf-svc-reference`, `PF_REFERENCE_API_KEY`, separate `PF_REFERENCE_DATABASE_URL`, the complete `RAT_* → REF_*` map, preservation of Python package `rates`, and authorized migration/cutover/cleanup execution. No mutation performed. | Owner decision recorded in conversation; artifact set and read-only inventory |
| 2026-11-21 | renamed | Owner selected `pf-svc-reference` as the canonical service identity; all IMP-013 artifacts were synchronized before execution. | Owner decision recorded in conversation; no service, database, or consumer mutation performed |
| 2026-11-21 | schema-renamed | Owner selected the `REF_` database prefix; all database mappings and execution references were synchronized before migration. | Owner decision recorded in conversation; no database mutation performed |
