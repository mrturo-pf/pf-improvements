# Plan: active service-name normalization

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: active `pf/improvements` metadata and workflow guidance.  
Approved: pending owner authorization

## 1. Inventory

- [ ] Run `python3 scripts/check-service-name-remnants.py` from the improvements
      repository root. The check is case-insensitive and scans both paths and content.
- [ ] Classify each match as historical evidence, stable identifier, generated output,
      active metadata, or current workflow guidance.
- [ ] Confirm the IMP-017 directory remains free of non-historical legacy mentions.
- [ ] Review filenames and directory names independently from file contents; a clean
      document with an obsolete filename is still a remaining alias.

## 2. Source identification

- [ ] Identify the source and generator for `improvements/improvements.json`.
- [ ] Identify whether current workflow aliases are referenced by any validation or CI
      contract.
- [ ] Confirm that record directory names and stable links are excluded from renaming.

## 3. Implementation

- [ ] Replace only active, non-historical occurrences using the approved mapping.
- [ ] Leave historical records, stable IDs, slugs, and links unchanged.
- [ ] Apply the complete approved alias-normalization mapping consistently; do not
      implement only a partial subset of the mapping.

## 4. Validation

- [ ] Run `python3 scripts/check-service-name-remnants.py` after implementation.
- [ ] Require exit code `0` for a strict scan once all permitted historical aliases have
      been migrated or explicitly removed from the selected validation scope.
- [ ] Run `python3 scripts/validate-improvements.py --write-generated`.
- [ ] Run `python3 scripts/validate-improvements.py`.
- [ ] Inspect the complete diff, including renames and deletions, not only content edits.
- [ ] Verify that remaining legacy occurrences are historical or stable identifiers.
- [ ] Record the final path/content inventory and validation results in this plan.

## 5. Rollback

Revert the active documentation/metadata change only. Generated files must be restored
by rerunning the repository generator, not by hand-editing generated output.

## 6. Closure criteria

The task may close when active guidance and metadata use current identities, all retained
legacy occurrences have a documented historical/stable reason, and validation passes.
