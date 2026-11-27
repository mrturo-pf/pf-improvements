# Plan: shared PF repository service-name normalization

Date: 2026-11-27  
Status: in progress  
Level: L  
Approved: owner authorized implementation on 2026-11-27.

## 1. Baseline and inventory

- [ ] Confirm target names: `pf-svc-common` and `pf-svc-gateway-proxy`.
- [ ] Capture clean status, branch, HEAD and remote URL for both source repositories and
      all consumer repositories.
- [ ] Inventory active references with path-aware, case-sensitive and URL-aware scans.
- [ ] Classify every old-name match as active, historical, generated, package/import,
      deployed resource, or task-definition self-reference.
- [ ] Save sanitized before-scan evidence under this record.

## 2. Repository rename

- [ ] Rename `pf-common` on GitHub to `pf-svc-common`, preserving `main`, branch rules,
      issues, releases, tags, and redirect behavior.
- [ ] Rename `pf-gateway-proxy` on GitHub to `pf-svc-gateway-proxy`, preserving the same
      controls and redirect behavior.
- [ ] Update local checkout directory names and `origin` URLs.
- [ ] Confirm `git ls-remote`, default branches, and GitHub redirects before changing
      consumers.

## 3. Active reference migration

- [ ] Update root `AGENTS.md`, `README.md`, `modules/INDEX.json` source inputs, and
      workspace metadata/scripts as applicable.
- [ ] Update architecture JSON sources and regenerate all affected HTML artifacts.
- [ ] Update Makefile includes, CI workflow references, documentation links and consumer
      checkout instructions in `pf-svc-income`, `pf-svc-reference`, and `pf-sheets`.
- [ ] Update gateway repository display/project metadata only where it represents the
      repository identity; preserve `pf_gateway_proxy` import paths unless separately
      approved.
- [ ] Regenerate `modules/INDEX.json` with `scripts/update-workspace.py`.
- [ ] Do not edit generated files manually.

## 4. Validation

- [ ] Run each affected repository's documented lint, unit, type, and integration checks.
- [ ] Run shared dependency/configuration validation and consumer Make checks.
- [ ] Run Archify validation and delivery for every changed architecture spec.
- [ ] Verify GitHub redirects, remote URLs, local paths, links, and branch tracking.
- [ ] Run the after-scan and classify every retained old-name occurrence.
- [ ] Inspect the complete cross-repository diff for accidental package, API, Cloud Run,
      service-account or database changes.

## 5. Delivery and rollback

- [ ] Deliver repository-specific changes through each repository's required PR workflow.
- [ ] Merge in dependency order: repository rename/remotes, active references, generated
      indexes/artifacts, then consumer documentation.
- [ ] Record PRs, validation results and any intentionally retained old names.
- [ ] Roll back by reverting active reference commits and restoring local remotes/paths;
      do not rewrite history or delete historical evidence.

## Closure criteria

The improvement may close when both repositories have the proposed canonical identities,
all active references and generated artifacts are aligned, consumer validation passes,
GitHub redirects/branch controls are verified, and the residual-name inventory is fully
classified.
