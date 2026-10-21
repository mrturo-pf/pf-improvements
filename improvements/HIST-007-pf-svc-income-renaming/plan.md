# Plan: rename `pf-payroll` to `pf-svc-income`

Date: 2026-10-05
Status: in progress
Level: L
Scope: Cross-repository/service identity rename and GCP migration.
Related artifacts: [investigation](investigation.md) · [brief](brief.md) · [recommendation](recommendation.md)
Approved: 2026-10-05 by a0a11b7 (conversation)
Superseded-by: none

> **Current phase: controlled implementation of the service-identity rename.** The physical `PAY_* → INC_*` schema migration and ORM compatibility slice are complete and validated in production. The service identity remains `pf-payroll`; repository/resource/consumer cutover work is now the active HIST-007 scope.

## 1. Status and gates

**Authorization boundary:** HIST-007 entered implementation on 2026-10-15 after
explicit authorization of code, dependencies, schema migration, Postman, GCP/IAM/
secrets, commits, pushes, deployment, cutover, and rollback. Production mutation
remains staged: local code/dependency slices come first; schema migration, GCP,
Postman cutover, deployment, and traffic cutover require their validation gates.

- [x] User decisions recorded.
- [x] Recommendation approved explicitly.
- [x] GitHub repository/workflow/environment inventory completed read-only.
- [x] Existing Cloud Run, Artifact Registry, Secret Manager, IAM, Scheduler, Logging, monitoring, and networking inventory completed to the extent permitted by the active account.
- [x] HTTP route, service API documentation, and Postman semantic comparison completed.
- [x] Local synthetic `pf-db` rename probe completed with transactional rollback and no persisted synthetic rows.
- [x] GitHub workflow/environment/history inventory completed read-only; repository and environment secret names were reviewed without reading values.
- [x] Environment-scoped secret inventory completed.
- [x] Cutover-relevant outcomes from `IMP-001` through `IMP-003` and `IMP-005` are resolved or explicitly accepted.
- [x] `IMP-004` shared-secret access review is released; its scoped secret-policy result is an accepted input.
- [x] `IMP-006` HTTP error baseline is released and available for release validation.
- [x] `IMP-007` Cloud Run observability/capacity baseline is closed with a documented bounded-evidence limitation accepted for cutover planning.
- [x] `IMP-008` identifier policy is validated; its release evidence is tracked separately and the policy applies to the physical migration.
- [x] Cloud Run URL policy and Postman target choice approved for the current service; the identity rename cutover remains pending.
- [x] Repository/code/schema implementation authorization received.
- [x] Schema migration, ORM alignment, deployment hardening, and production smoke validation completed.
- [x] Cross-repository commits/pushes and deployment execution authorized and validated for the compatibility slice.
- [ ] Repository rename to `pf-svc-income` completed.
- [ ] New service identity, GCP resources, secrets, URLs, and Postman consumers cut over.
- [ ] Rollback window of 14 calendar days (or until one representative payroll flow
  completes, whichever is longer) approved and evidenced for the identity cutover.

The lifecycle state is `in progress`: the schema/ORM compatibility slice is complete,
while the approved service-identity rename remains active. External security, access,
error-baseline, observability, and identifier-policy inputs are consumed as evidence,
not treated as blockers.

## 1.1 Latest evidence and blockers (2026-10-15)

Inventory confirms that the current `pf-payroll` service remains active and the
`pf-svc-income` target resources do not exist. Rename-specific blockers remain
consumer inventory, URL cutover, schema migration validation, package-boundary
review, and explicit authorization.

The following external outcomes are now available and must be reused rather than
reopened:

- `IMP-001` is released; Scheduler credential remediation and cleanup are complete.
- `IMP-002` is released; backup/restore, runtime cutover, sensitive-artifact cleanup,
  and ownership migration are complete, with the documented Neon provider-role
  residual risk accepted.
- `IMP-003` is superseded by `IMP-002`; no duplicate role-hardening work is needed.
- `IMP-005` is released; WIF deployments succeeded and legacy deploy keys/grants were
  removed.
- `IMP-008` is validated/released; its identifier policy applies to the new `pf-db`
  migration and physical rename.
- `IMP-009` is released; Scheduler OIDC and the authenticated `/execute` path are
  validated with HTTP 200.

The previously external gates are now resolved inputs: `IMP-004` is released,
`IMP-006` is released, `IMP-007` is closed with its bounded-evidence limitation
accepted, `IMP-008` is validated/released, and `IMP-009` is released. `IMP-003` is
superseded by `IMP-002`. None of these improvements is an active blocker for the
rename proposal; their documented limitations and release evidence must still be
reused during cutover validation.

Rename-specific blockers are consumer inventory, URL cutover, schema migration
validation, package-boundary review, and explicit authorization.

## 1.2 Read-only validation — 2026-10-15

### Consumer and URL reconciliation

- The live Cloud Run service is `pf-payroll`, URL
  `https://pf-payroll-yqd4p7fzaa-uc.a.run.app`, ready revision
  `pf-payroll-00064-7s7`, using runtime identity
  `pf-payroll@coreassistant-474022.iam.gserviceaccount.com`.
- The committed GCP Postman environment still points `pf-payroll-url` to
  `https://pf-payroll-646185261155.us-central1.run.app` and retains the
  `pf-payroll-api-key` variable. This is a stale target/identity contract that
  must be reconciled before a rename cutover; no Postman mutation was made.
- The collection uses `{{pf-payroll-url}}` and `{{pf-payroll-api-key}}` across the
  payroll request group. The target migration must update the collection and both
  environments together, preserving the `/payroll/*` route family.
- Read-only repository search found no evidence that `pf-rates` or `pf-sheets`
  calls the payroll service directly at runtime; their remaining references are
  documentation or ecosystem metadata and still require intentional review.

### Schema migration validation

- `pf-db` migration `0003_rename_tables_service_prefix.py` establishes the current
  `PAY_*` tables and `PAY_MV_SUMARY`; no `PAY_* → INC_*` migration exists yet.
- The current `make identifier-check` passes for 36 identifiers. This validates the
  existing policy only; it does not validate the proposed physical rename.
- The proposed migration still requires a hand-written Alembic upgrade/downgrade,
  representative existing-data validation, explicit dependent-index/constraint/
  sequence/materialized-view checks, and consumer ORM compatibility checks.
- No database mutation or migration execution was performed in this validation.

### Package-boundary review

- `pf-payroll` has no `src/income` package yet. Its current dependency direction is
  internally layered, and `payroll.domain` has no SQLAlchemy/http client imports.
- Initial extraction candidates remain `domain/quantizers.py`, `domain/deflation.py`,
  and narrowed market-data resolution ports/helpers. Payroll repositories, models,
  payroll-period DTOs/use cases, employer/contracts, insurance, tax, PDF, and import
  flows remain payroll-specific.
- `pf-common/scripts/sync_deps.py` currently fails because SQLAlchemy constraints
  differ: `pf-payroll` pins `sqlalchemy>=2.0.36,<2.1`, while `pf-rates` declares
  `sqlalchemy>=2.0.36`. Dependency alignment is required before sharing package
  infrastructure or treating the package split as complete.

These findings narrow the active HIST-007 blockers to stale consumer/URL contracts,
the physical schema migration, package-boundary implementation, dependency alignment,
and the existing authorization/cutover gates. External improvement prerequisites
remain resolved inputs.

## 1.3 Decision package prepared — implementation not authorized

### Consumer and URL decision

- Treat the current Cloud Run URL as evidence of the existing service only; do not
  copy it to the renamed service. The future deployment must publish the target URL
  from Cloud Run and use that value consistently.
- Adopt `pf-svc-income-url` and `pf-svc-income-api-key` as the future Postman variable
  names. Keep `/payroll/*` routes unchanged in this rename.
- Update the collection and LOCAL/GCP environments in one Postman change after the
  target URL and secret are explicitly approved. Do not add a compatibility alias
  unless the rollback decision requires it and the alias has an expiry date.
- Current evidence identifies Postman as the direct functional consumer surface;
  repository references in `pf-common`, `pf-db`, and service docs are documentation,
  workflow, or ownership references. No direct runtime caller from `pf-rates` or
  `pf-sheets` was identified in the read-only search, but the cutover checklist must
  re-run the search after target URLs are decided.

### Migration design decision

The future `pf-db` migration must be a hand-written, reversible Alembic migration:

1. Assert the expected `PAY_*` objects and columns exist; fail before mutation if
   the baseline differs.
2. Enter the approved maintenance boundary and prevent application traffic from
   writing during the rename.
3. Rename tables, dependent semantic columns, sequences, indexes, constraints, and
   the materialized view explicitly. Recreate the view with `INC_*` names and the
   corrected `INC_MV_PAY_SUMMARY` identifier.
4. Validate catalog metadata, row counts, primary/foreign keys, sequence ownership,
   view columns, ORM mappings, and representative queries.
5. Release traffic only after the new service passes smoke tests.
6. Provide a downgrade that restores the complete `PAY_*` vocabulary and view
   definition without data copying or destructive recreation.

The migration must not add a generic income ledger, nullable honorarios fields, or
new business behavior. `PAY_PERIOD → INC_PAYROLL`, `period_id → payroll_id`, and
`period_year/month → accrual_year/month` remain approved semantic changes.

### Package-boundary decision

Create `income` only for pure or port-based capabilities with no payroll persistence
or payroll route dependency. The first extraction slice should be limited to
quantization/deflation primitives and a narrowed market-data port after tests prove
that their DTOs and names are not payroll-specific.

Keep persistence, payroll DTOs, payroll periods, employers/contracts, insurance,
monthly employment tax, PDF, import/reconciliation, and payroll use cases in
`payroll`. Enforce `payroll → income`; `income` must not import payroll infrastructure.

Before extraction, align the SQLAlchemy constraint mismatch reported by
`pf-common/scripts/sync_deps.py`; do not silently broaden the `pf-payroll` constraint.
The alignment decision requires tests in both services and an explicit dependency
owner.

### Compatibility decisions to capture

- URL: use the service-generated target URL; no custom domain is proposed for this
  rename because none exists today. **Approved 2026-10-15.**
- API key: use an atomic `PF_PAYROLL_API_KEY → PF_INCOME_API_KEY` cutover with no
  application fallback. **Approved 2026-10-15.**
- Schema: use a short maintenance boundary rather than a compatibility bridge;
  this avoids dual ORM/schema semantics. **Approved 2026-10-15.**
- Rollback: retain old service/schema/secret for 14 days or one representative
  payroll flow, whichever is longer. **Approved 2026-10-15.**
- Postman: update collection and both environments atomically after the target URL
  and secret are created and approved. **Approved 2026-10-15.**
- Dependencies: align SQLAlchemy constraints explicitly across the affected services
  and validate both before package extraction. **Approved 2026-10-15.**

### Future implementation authorization record

The following approvals must be captured separately before Phase 3:

- [ ] authorize code/package changes in `pf-payroll`;
- [ ] authorize the `pf-db` migration and maintenance boundary;
- [ ] authorize Postman collection/environment changes;
- [ ] authorize new GCP Artifact Registry, Cloud Run, service account, and secrets;
- [ ] authorize consumer cutover and rollback window;
- [ ] authorize commits/pushes and deployment approvals for each affected repo.

Until every applicable item is explicitly approved, this package remains design and
investigation evidence only.

## 1.4 Required execution order

This order is normative for the proposal. Phase 1 is read-only. Approval gates are
recorded before Phase 3 mutations; external follow-ups remain in the register.


### Phase 1 — Safe investigation, without mutations

1. Identify known consumers through authorized logs, Postman, repositories,
   workflows, jobs, and configuration.
2. Reconcile current and historically advertised Cloud Run URLs, including the
   Postman-configured URL, without assuming that either is stale.
3. Validate the approved API, package, schema, migration, and rollback contracts.
4. Record any unrelated finding in the ecosystem improvement register instead of
   expanding this plan.

### Phase 2 — Decisions and approvals

Approve the rename-specific package, schema, API, consumer, cutover, and rollback
contracts. Resolve or explicitly accept the registered external gates before Phase 3.

### Phase 3 — Controlled changes, with explicit authorization

1. Apply only approved consumer, repository, package, schema, and Postman changes.
2. Apply the reversible `pf-db` migration before traffic uses the new ORM names.
3. Deploy `pf-svc-income` with immutable identity and approved settings.
4. Execute representative synthetic smoke tests and monitor the approved rollback
   window.
5. Handle external security and operations gates through their registered entries.

No target resource, database migration, consumer cutover, or deployment is
authorized merely because it appears in this plan.

## 1.5 Phase 2 decision package

The following decisions are prepared from the Phase 1 evidence. They are proposals for explicit approval, not executed changes. No credential rotation, IAM mutation, resource creation, schema migration, consumer update, or deployment is authorized by this section alone.

### Out-of-scope operational and security follow-ups

The following findings are not part of the rename design. They are registered in
[`../../index.md`](../../index.md)
and remain separate workstreams:

- `IMP-001` — Scheduler credential exposure and incident response;
- `IMP-002` — Neon credential, backup, restore, and sensitive-dump hardening;
- `IMP-003` — least-privilege database runtime roles;
- `IMP-004` — `pf-rates` access to `PF_DATABASE_URL`;
- `IMP-005` — deployer/runtime identity separation and WIF;
- `IMP-006` — ecosystem HTTP error baseline;
- `IMP-007` — Cloud Run observability and capacity standards.

The rename remains blocked by the directly relevant gates from these workstreams,
but their detailed investigation, remediation, and reusable standards do not belong
in this plan. Keep only the gate result and a link here.

### Schema maintenance window

**Proposal:** use a short maintenance boundary rather than a zero-downtime physical rename.

Before the window:

- backup and restore readiness from `IMP-002` is confirmed;
- the deterministic contract parity suite is run against `pf-payroll`;
- Postman target variables are prepared without changing active consumers;
- if startup does not validate schema, the new image may be deployed before the window with no traffic.

During the window:

1. stop known consumers and isolate old traffic using an approved reversible mechanism;
2. wait at least the request timeout (`300s`) for in-flight requests to drain;
3. capture the pre-migration backup and schema/row-count snapshot;
4. apply the reversible `pf-db` migration;
5. recreate `INC_MV_PAY_SUMMARY` with `payroll_id`, `accrual_year`, and `accrual_month`;
6. run catalog, row-count, and aggregate assertions;
7. deploy or activate the compatible service image;
8. run Go/No-Go smoke tests before enabling consumers.

Maximum duration and abort criteria must be approved before execution. Do not use `--ingress=internal` as an automatic step until the invoker/ingress model and rollback procedure are confirmed; it is a candidate isolation mechanism, not an executed instruction.

Status: pending `IMP-002` backup/restore readiness and operational approval.

### Rollback window

**Proposal:** retain rollback capability for **14 calendar days and until one representative monthly payroll flow completes**, whichever is longer. Define the flow as import, review/summary, and export using synthetic or explicitly approved operational data.

During the window:

- retain the old service, image, account, and `PF_PAYROLL_API_KEY`;
- retain the old account's access to the old secret until closure;
- keep the old service at scale-to-zero and isolated from normal traffic;
- freeze `pf-db` migrations touching `INC_*` objects and dependencies;

Rollback is not merely redirecting traffic: stop the new service, run the tested schema downgrade, verify the original `PAY_*` schema and `PAY_MV_SUMARY` columns, restore old-service access, and run the parity suite. New migrations during the window invalidate this downgrade path unless explicitly re-approved.

Status: pending approval of observation period, flow definition, and freeze policy.

### Contract parity and release acceptance

The rename must compare the old and new service for health, authentication, reads,
imports, PDF preview, exports, reference data, and approved error cases. The
reusable HTTP error taxonomy and observability baseline are tracked as `IMP-006`.
Cloud Run alerting, probes, capacity limits, and database connection-budget
standards are tracked as `IMP-007`.

For this rename, the acceptance gate is limited to:

- approved contract differences are documented;
- generated OpenAPI, `docs/api.md`, Postman, and route definitions agree;
- representative synthetic flows pass against the renamed service;
- no unexplained regression is introduced by the cutover.

### Database change freeze

**Proposal:** from cutover until rollback closure, do not merge migrations touching `INC_*` objects or dependencies. An emergency exception must explicitly restate or invalidate the downgrade path.

Status: pending approval.

### Decision 12 — Invocation and URL compatibility

Verify the target service's invocation policy and preserve the approved URL and
API-key cutover behavior. Do not assume either currently advertised URL is stale;
reconcile it with consumers and Postman before cutover. Broader IAM and ingress
standards are tracked through `IMP-005` and `IMP-007`.

Status: pending URL evidence and approval.

### Related database security work

The rename must not broaden database privileges or bypass the current `pf-db`
identifier policy. Runtime-role hardening is tracked as `IMP-003`; Neon credential,
backup, and restore hardening is tracked as `IMP-002`; and the identifier-length
policy is tracked as `IMP-008`. The policy is validated and applies to the
physical migration; only release evidence remains pending. Their detailed designs
belong in their own proposals.

### Phase 2 gate

Phase 3 remains blocked until the rename-specific decisions are approved and the
still-open gates that affect the selected release stage are resolved or explicitly
accepted. The released outcomes of `IMP-001`, `IMP-002`, and `IMP-005`, the
supersession of `IMP-003`, and the validated `IMP-008` policy are already accepted
inputs; they are not pending remediation. Preparing this package does not rotate
credentials, change IAM, create GCP resources, alter the database, update Postman,
or deploy a service.

## 2. Decisions to record before implementation

- [x] GitHub repository target is `mrturo-pf/pf-svc-income`.
- [x] Local folder target is `modules/pf-svc-income`.
- [x] Retain `payroll` for payroll-specific behavior and add a second shared package; recommended name `income`.
- [x] Runtime/API key target is `PF_INCOME_API_KEY`.
- [x] Existing `/payroll/*` HTTP routes remain; detail route is `/payroll/{payroll_id}`.
- [x] Existing `PAY_*` objects are renamed through `pf-db`; `PAY_PERIOD → INC_PAYROLL`.
- [x] Exact `INC_*` target map is approved, subject to migration implementation validation.
- [x] `PAY_MV_SUMARY` target is explicitly `INC_MV_PAY_SUMMARY` (18 ASCII characters), correcting `SUMARY` to `SUMMARY` and making the payroll domain explicit.
- [x] `IMP-008` identifier policy is validated; apply it to the physical migration and retain release evidence separately.
- [ ] Review all generated and explicit index/constraint names for uniqueness and a maximum of 63 bytes; no automatic truncation.
- [x] No custom domain/DNS behavior is involved.
- [x] API key migration is atomic: target `PF_INCOME_API_KEY`; no application fallback to `PF_PAYROLL_API_KEY`.
- [ ] Rollback exit criteria and observation period are approved.

## 3. Implementation slices

### Slice 0 — Close evidence gaps and freeze design decisions

Repositories/files:

- actual GCP resources and service configuration recorded;
- GitHub repository settings, secrets, environments, webhooks, branch protection;
- external consumer and log inventory;
- Postman workspace/environment inventory;
- database role/backup/monitoring reference scan;
- exact package split and dependency boundary;
- exact `INC_*` target map;
- ORM/DTO/route vocabulary migration (`period_id → payroll_id`, period-oriented DTOs → payroll-oriented DTOs);
- API-key atomic cutover;
- schema cutover/rollback compatibility strategy.

- Actual resources and consumers are recorded in the investigation or its dated change log.
- No secret values are copied into artifacts.
- Unknowns affecting cutover are either resolved or explicitly blocked.

### Slice 1 — Coordination metadata

Files:

- root `index.md`;
- this plan and related artifacts.

Exit criteria:

- Slug is registered with Level L, owner `pf-base`, affected repositories, status, and links.

### Slice 2 — Shared tooling preparation

Repository: `pf-common`.

Expected changes:

- workflow comments/examples mentioning `pf-payroll`;
- path-based dependency synchronization script and messages;
- README/reference paths;
- any allowlists or service-name assumptions.

Exit criteria:

- Shared workflow syntax and script tests pass.
- No behavior change for `pf-rates`.

### Slice 3 — Database migration and ownership documentation

Repository: `pf-db`.

Expected changes:

- add a reversible hand-written migration renaming the approved `PAY_*` objects to the `INC_*` map (maximum 30 characters), including `PAY_PERIOD → INC_PAYROLL` and the full PDF-template names;
- rename relationship columns from `period_id` to `payroll_id` and temporal columns from `period_year`/`period_month` to `accrual_year`/`accrual_month`;
- preserve all `id` PKs, `BIGSERIAL` sequences, monetary types, enums, nullability, defaults, rows and IDs;
- explicitly audit/rename PK/FK/unique/check constraint names, indexes, sequence ownership, materialized-view definition/columns, seeds, restore scripts and inspection SQL; keep explicit index/constraint names below PostgreSQL's 63-byte limit and do not rely on automatic truncation;
- use a short maintenance boundary unless a separately designed compatibility bridge is approved;

Exit criteria:

- migration upgrades and downgrades cleanly on a fresh database;
- migration runs against synthetic existing data without row/ID loss;
- all FKs, indexes, constraints, materialized-view semantics and seeds are verified;
- ORM/application code is not deployed against `INC_*` until this migration is available.

### Slice 4 — Service source identity and package split

Repository after rename: `pf-svc-income`.

Expected changes:

- rename repository/folder through approved GitHub/local procedure;
- update `pyproject.toml` distribution metadata to `pf-svc-income`;
- retain `src/payroll` for payroll-specific modules;
- add `src/income` for extracted generic capabilities only;
- move/re-home quantizers, generic deflation, market-data ports/resolution, and reviewed generic DTOs;
- keep payroll import/reconciliation, payroll repositories, employer/contracts, contributions, employment tax, PDF, and payroll exports in `payroll`;
- update only affected imports, package data, tests, diagrams, and Docker packaging;
- update ORM table names to the approved `INC_*` names;
- rename period-oriented DTOs to payroll-oriented DTOs (`PayrollPeriodDetailDTO → PayrollDetailDTO` and equivalent range/import DTOs);
- update `period_id` to `payroll_id` across commands, ports, DTOs and route handlers;
- update collection fields where they represent payroll entities (`periods[] → payrolls[]` where applicable);
- update the detail route metadata and handler to `/payroll/{payroll_id}` while preserving concrete URLs;
- resolve `period_year`/`period_month` naming as `accrual_*` based on the semantic review;
- update config naming and perform the atomic `PF_INCOME_API_KEY` cutover;
- preserve the `/payroll/*` route family;

Exit criteria:

- `payroll` imports remain valid.
- `income` imports successfully and does not import payroll infrastructure.
- Architecture/dependency tests enforce `payroll → income`, never the reverse.
- Full service tests and static-quality checks pass.
- Docker image starts and `/health` works against the migrated schema.

### Slice 5 — Service docs and operational configuration

Repository: `pf-svc-income`.

Expected changes:

- `README.md`, `AGENTS.md`, getting-started, development, deployment, database, API, workflow docs;
- workflow `repo_name`/`service_name` inputs;
- GCP setup comments and resource names;
- local environment examples and secrets README;
- operational rollback/runbook references.

Exit criteria:

- Docs distinguish service identity `pf-svc-income` from payroll route/domain vocabulary.
- No credentials or real personal data are added.

### Slice 6 — Root ecosystem, Postman, and architecture

Repository: `pf-base`.

Expected changes:

- root README/AGENTS current references;
- Postman collection folder and variables;
- local/GCP Postman environments with the new base URL after deployment evidence;
- architecture JSON sources, links, labels, generated HTML via the documented generator;
- root diagrams/index references.

Exit criteria:

- JSON parses.
- OpenAPI and Postman agree on current `/payroll/*` paths.
- Generated architecture output matches source.

### Slice 7 — GCP parallel resources and schema-aware deployment

Operations/GCP, only after explicit authorization.

Expected actions:

- create new Artifact Registry repository;
- create new service account and least-privilege IAM;
- create/populate new API-key secret without exposing the value;
- grant access to shared secrets;
- build/push immutable image tags;
- deploy Cloud Run service with existing cost/scaling policy.

Exit criteria:

- New resource names, revisions, traffic, IAM, secrets, region, min/max instances, and logs are recorded.
- `/health` and authenticated synthetic smoke tests pass.

### Slice 8 — Consumer cutover and rollback window

Expected actions:

- update known Postman/clients/configuration;
- verify no old service traffic remains except expected compatibility traffic;
- monitor logs, errors, latency, database behavior, and rates calls;
- verify the new service is running against `INC_*` after the migration;
- verify old-service rollback behavior before removing old schema compatibility;
- retain old service/resources for the approved evidence window.

Exit criteria:

- New service is authoritative for the intended consumers.
- Rollback to old service is tested/documented.
- No manual deployment gate was approved without explicit user authorization.

### Slice 9 — Cleanup and closure

Expected actions, only after approval:

- remove old secret access/old service account;
- delete or retain old Cloud Run service and Artifact Registry repository per retention decision;
- finalize docs and proposal status;
- record commits, workflow run IDs, deployment URL, smoke results, and follow-ups.

Exit criteria:

- No unresolved old identity references except intentional historical/compatibility references.
- Index status is `released`, `validated`, `blocked`, or `closed` with evidence.

## 4. Validation command checklist

Commands are examples and must be run from the correct repository after reading its current instructions:

- reference scan for `pf-payroll`, `PF_PAYROLL`, `src/payroll`, and old URLs;
- service `make check` and Docker build/health validation;
- `python -c` package import check;
- `alembic upgrade head` and `alembic check` in `pf-db` test environment;
- JSON parse checks for Postman and architecture files;
- generated OpenAPI versus `docs/api.md` comparison;
- CI workflow validation;
- authorized GCP `gcloud` describe/list checks;
- authorized GitHub `gh` workflow/run checks only after `source "$HOME/Documents/scripts/unset_proxies.sh"` and unsetting certificate overrides as required by repository instructions.

## 5. Change log

| Date | Status | Change | Reason/evidence |
|---|---|---|---|
| 2026-10-05 | planned | Created the Level L investigation, brief, recommendation, and living plan. | Workflow-compliant planning; no code or infrastructure mutation. |
| 2026-10-07 | investigating | Completed rename-relevant route, consumer, Postman, schema, and deployment-identity inventory. | Read-only evidence; target identity does not yet exist. |
| 2026-10-07 | validating | Completed the local synthetic schema-rename and rollback probe. | `pf-db` migration shape remains implementation work. |
| 2026-10-10 | blocked | Moved unrelated security, IAM, backup, error-baseline, and observability findings to `IMP-001` through `IMP-007`. | Scope control; detailed follow-ups belong in the ecosystem register. |
| 2026-10-15 | investigating | Completed read-only consumer/URL, schema, and package-boundary validation. Found stale Postman payroll URL/variable contracts, no `INC_*` migration yet, no `src/income` package yet, and a SQLAlchemy dependency mismatch in `pf-common` sync validation. | Live Cloud Run metadata, Postman GCP environment, `pf-db` migration `0003`, `make identifier-check`, `pf-common/scripts/sync_deps.py` |
| 2026-10-15 | investigating | Prepared the consumer/URL, reversible migration, package-boundary, compatibility, and authorization decision package. Decisions 1–6 were approved; Phase 3 execution remains unauthorized pending the separate operational authorization record. | This section; design and recommendation artifacts |
| 2026-10-15 | in progress | Started the first implementation slice: aligned SQLAlchemy constraints, fixed the async export-job read path, and introduced `income.domain` quantization/deflation with compatibility exports and tests. | `pf-common` sync passed; `pf-payroll` 571 tests passed; `pf-rates` targeted regression passed |
| 2026-10-15 | in progress | Added the reversible `pf-db` migration `0017` for the `PAY_* → INC_*` rename. Local PostgreSQL upgrade, downgrade to `0016`, and re-upgrade passed; catalog checks confirmed `INC_PAYROLL`, `INC_PAY_ITEM`, `INC_MV_PAY_SUMMARY`, `payroll_id`, `accrual_year`, and `accrual_month`. | `pf-db` commit `7a5caa9`, branch `hist-007-schema-inc-migration` |
| 2026-10-15 | in progress | Initial ORM rename probe was intentionally not published: 562 payroll tests passed but 9 compatibility tests exposed existing test/repository coupling to `PAY_*` and fake-session result shapes. The models were restored; ORM, repository, and test updates must land as one coordinated slice. | Local payroll test run; no additional working-tree changes retained |


## 6. Release record — schema/ORM compatibility slice

### Commits and migrations

- `pf-db`: migration `0017` implements the reversible `PAY_* → INC_*` rename; the production dump reports Alembic head `0018`.
- `pf-payroll`: `163833e feat(payroll): align ORM with income schema (#5)` aligns the ORM to `INC_*` objects.
- `pf-rates`: `054e376 fix(rates): map economic index to accrual columns (#7)` aligns rates period semantics with the renamed schema vocabulary.
- `pf-common`: deployment hardening includes immutable image deployment, schema checks, protected-smoke diagnostics, and revision-readiness handling; the final implementation is tracked through PRs `#12`, `#13`, and the follow-up revision-readiness fix.

### Database dump evidence

`modules/pf-db/secrets/neon_dump.sql` was inspected read-only. It contains:

- `INC_EMPLOYER`, `INC_EMP_CONT`, `INC_PAYROLL`, `INC_PAY_CONCEPT`, `INC_PAY_ITEM`, and related `INC_*` objects;
- no `PAY_EMPLOYER` table;
- `alembic_version = 0018`.

This confirms the database was correct; the observed `PAY_EMPLOYER` failure came from stale container code/revision selection, not a missing production migration.

### Cloud Run and workflow evidence

- `pf-rates` deployment workflow run `39531595670`, final attempt `5`, completed successfully.
- `pf-payroll` deployment workflow run `39532026048`, final attempt `9`, completed successfully.
- The failed attempts exposed stale-image reuse, mutable-tag redeployment, Cloud Run eventual-consistency revision selection, WIF/IAM smoke authentication, and missing protected-smoke diagnostics. These were corrected in the reusable `pf-common` workflow.

### Final smoke results

- `pf-rates`: pipeline and database-backed endpoints passed after the immutable-image and schema verification changes.
- `pf-payroll`: `/health` and authenticated `/payroll/employers` passed after deployment selected the newly created Ready revision containing `INC_EMPLOYER`.
- Protected smoke now records the response body (bounded and without API-key values) on non-2xx responses.

### Current state and next phase

The physical schema rename and ORM compatibility slice are complete. The active work is the
service-identity rename to `pf-svc-income`: repository/package identity, GCP resources,
secrets, URLs, Postman variables, consumer cutover, rollback window, and cleanup.

## 7. Implementation problems and corrections

| Problem | Evidence | Correction |
|---|---|---|
| Old image queried `PAY_EMPLOYER` against an `INC_*` database | Cloud Run `UndefinedTableError`; image inspection showed old ORM | Rebuilt with schema verification and no release cache |
| Same commit tag hid a new image digest | Reruns reused `:<github.sha>` | Deploy by Artifact Registry immutable digest |
| Cloud Run selected an older Ready revision | Traffic returned to `pf-payroll-00064-7s7` while newer revisions existed | Use `latestCreatedRevisionName`, wait for `Ready=True`, then update traffic |
| Protected smoke WIF/IAM failed | Missing deployer Secret Manager access and redundant second WIF exchange | Grant least-privilege accessor; run protected smoke in authenticated deploy job |
| Smoke failure hid application body | Only HTTP 500 was printed | Capture bounded response body without secrets |

## 8. Final summary for this phase

Completed: reversible schema rename, production schema application, ORM alignment, image/schema
verification, immutable deployment, Cloud Run readiness handling, IAM correction, and final
HTTP smoke validation. Pending: the approved `pf-payroll → pf-svc-income` service-identity
rename and its consumer cutover/rollback/cleanup evidence.
