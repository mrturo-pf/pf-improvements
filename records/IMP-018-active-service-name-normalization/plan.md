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
      active metadata, current workflow guidance, or task-definition self-reference.
- [ ] Confirm IMP-017 contains aliases only in the auditable equivalence-table
      self-reference; it must not contain unrelated active remnants.
- [ ] Review filenames and directory names independently from file contents; a clean
      document with an obsolete filename is still a remaining alias.

## 2. Source identification

- [ ] Identify the source and generator for `improvements/improvements.json`.
- [ ] Identify whether current workflow aliases are referenced by any validation or CI
      contract.
- [ ] Confirm from the workspace/module index that affected repository values map to
      current repository identities, while historical infrastructure names remain out
      of scope.
- [ ] Confirm that historical record directory names and stable links are excluded from
      renaming, while any active filename/path rename is checked for inbound references.

## 3. Implementation

- [ ] Replace only active, non-historical occurrences using the approved mapping.
- [ ] Leave historical records, stable IDs, slugs, and links unchanged.
- [ ] Apply the complete approved alias-normalization mapping consistently; do not
      implement only a partial subset of the mapping.
- [ ] Review compound matches such as longer names and URLs manually before replacing
      them; discovery is substring-based and case-insensitive, replacement is not blind.
- [ ] Leave the equivalence table and its explanatory self-references intact.

## 4. Validation

- [ ] Run `python3 scripts/check-service-name-remnants.py` after implementation.
- [ ] Treat a non-zero full-tree result as an inventory requiring manual
      classification; do not ignore or auto-allow historical findings.
- [ ] Run `python3 scripts/validate-improvements.py --write-generated`.
- [ ] Run `python3 scripts/validate-improvements.py`.
- [ ] Inspect the complete diff, including renames and deletions, not only content edits.
- [ ] Verify that remaining legacy occurrences are historical or stable identifiers.
- [ ] Save the pre-change and post-change checker output as versioned evidence under
      this IMP-018 record, then summarize the classification in this plan.
- [ ] Do not execute implementation or rename paths while this plan remains
      `Approved: pending owner authorization`. Owner authorization is a prerequisite.

## 5. Rollback

Revert the active documentation/metadata change only. Generated files must be restored
by rerunning the repository generator, not by hand-editing generated output.

## 6. Closure criteria

The task may close when owner authorization exists, active guidance and metadata use
current identities, every retained legacy occurrence has a documented historical/stable
or task-definition reason, active filenames and paths have been reviewed, and both
validation commands pass. A full-tree non-zero remnant scan is acceptable only when
every reported finding is classified in the final before/after inventory.
