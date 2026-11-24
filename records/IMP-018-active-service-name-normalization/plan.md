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
- [ ] Confirm that historical record directory names and stable links are excluded from
      renaming, while any active filename/path rename is checked for inbound references.

## 3. Implementation

- [ ] Replace only active, non-historical occurrences using the approved mapping.
- [ ] Leave historical records, stable IDs, slugs, and links unchanged.
- [ ] Apply the complete approved alias-normalization mapping consistently; do not
      implement only a partial subset of the mapping.

## 4. Validation

- [ ] Run `python3 scripts/check-service-name-remnants.py` after implementation.
- [ ] Treat a non-zero full-tree result as an inventory requiring manual
      classification; do not ignore or auto-allow historical findings.
- [ ] Run `python3 scripts/validate-improvements.py --write-generated`.
- [ ] Run `python3 scripts/validate-improvements.py`.
- [ ] Inspect the complete diff, including renames and deletions, not only content edits.
- [ ] Verify that remaining legacy occurrences are historical or stable identifiers.
- [ ] Record the final path/content inventory and validation results in this plan.

## 5. Rollback

Revert the active documentation/metadata change only. Generated files must be restored
by rerunning the repository generator, not by hand-editing generated output.

## 6. Closure criteria

The task may close when active guidance and metadata use current identities, every
retained legacy occurrence has a documented historical/stable reason, active filenames
and paths have been reviewed, and both validation commands pass. A full-tree non-zero
remnant scan is acceptable only when every reported historical/stable finding is
classified in the final inventory.
