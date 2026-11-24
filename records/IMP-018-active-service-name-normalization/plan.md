# Plan: active service-name normalization

Date: 2026-11-24  
Status: completed
Level: M  
Scope: active `pf/improvements` metadata and workflow guidance.  
Approved: owner authorization received on 2026-11-24

## 1. Inventory

- [x] Run `python3 scripts/check-service-name-remnants.py` from the improvements
      repository root with `--exclude-path records/IMP-018-active-service-name-normalization/evidence`.
      The check is case-insensitive and scans both paths and content.
- [x] Classify each match as historical evidence, stable identifier or historical path,
      generated output, active metadata, current workflow guidance, or task-definition
      and evidence self-reference.
- [x] Confirm IMP-018 contains aliases only in the auditable equivalence-table or
      task-definition/evidence self-reference; it must not contain unrelated active
      remnants.
- [x] Review filenames and directory names independently from file contents; no active
      filename/path rename was required.

## 2. Source identification

- [x] Identify the source and generator for `improvements/improvements.json`: the root
      manifest is the editable source and `generated/` is derived output.
- [x] Identify whether current workflow aliases are referenced by any validation or CI
      contract.
- [x] Confirm from the workspace/module index that affected repository values map to
      current repository identities, while historical infrastructure names remain out
      of scope.
- [x] Confirm that historical record directory names and stable links are excluded from
      renaming, while any active filename/path rename is checked for inbound references.

## 3. Implementation

- [x] Replace only active, non-historical occurrences using the approved mapping.
- [x] Leave historical records, stable IDs, slugs, and links unchanged.
- [x] Apply the complete approved alias-normalization mapping consistently; do not
      implement only a partial subset of the mapping.
- [x] Review compound matches such as longer names and URLs manually before replacing
      them; discovery is substring-based and case-insensitive, replacement is not blind.
- [x] Leave the equivalence table and its explanatory self-references intact.

## 4. Validation

- [x] Run `python3 scripts/validate-improvements.py --write-generated` first so generated
      metadata reflects the normalized source.
- [x] Run `python3 scripts/validate-improvements.py` before the after-scan.
- [x] Run `python3 scripts/check-service-name-remnants.py` after those regeneration and
      validation commands, excluding the versioned `evidence/` output directory so the
      checker does not read prior inventories as new source findings.
- [x] Preserve the checker exit code in each inventory output. Both scans returned `1`
      with no skipped files; no `2` or exception occurred.
- [x] Treat a non-zero full-tree result as an inventory requiring manual
      classification; do not ignore or auto-allow historical findings.
- [x] Inspect the complete diff, including renames and deletions, not only content edits.
- [x] Verify that remaining legacy occurrences are historical, stable identifiers,
      generated output whose source is historical/permitted, or task-definition/evidence
      self-references; all active metadata and current workflow findings must be
      normalized.
- [x] Save the pre-change and post-change checker output as versioned evidence under
      this IMP-018 record using a temporary file outside the repository, then move it
      into `evidence/` only after the checker exits. Summarize the classification in
      this plan.

## 5. Rollback

Revert the active documentation/metadata change only. Generated files must be restored
by rerunning the repository generator, not by hand-editing generated output.

## 6. Closure criteria

The task may close when owner authorization exists, active guidance and metadata use
current identities, every retained legacy occurrence has a documented historical/stable, generated-from-
permitted-source, or task-definition/evidence reason, active filenames and paths have been reviewed, and both
validation commands pass. A full-tree non-zero remnant scan is acceptable only when
every reported finding is classified in the final before/after inventory, and generated
output is accepted only when its source is historical/permitted rather than active.
