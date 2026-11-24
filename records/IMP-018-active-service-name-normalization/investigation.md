# Investigation: active service-name normalization

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: `pf/improvements` active metadata and workflow guidance.

## Finding

The IMP-018 artifact directory contains the requested legacy aliases only where this
IMP-018 brief defines and explains the equivalence table; those are task self-references,
not service metadata or operational guidance. The broader improvements repository
contains occurrences that must be classified using the same six categories throughout
this task:

- historical evidence;
- stable identifier or historical path;
- generated output;
- active metadata;
- current workflow guidance;
- task-definition and evidence self-reference.

### Historical and permitted

Occurrences in `records/HIST-*` and completed improvement records document former
repositories, resources, migrations, or historical implementation state. They are
retained as evidence and must not be rewritten by this task.

Record names and stable slugs may also preserve former terminology because changing
them would break links and artifact history.

### Task-definition self-reference and permitted

The equivalence table in this task's brief, plus task-definition and evidence files that
record its scan output or classifications, may retain legacy spellings so the mapping is
auditable. This is a dedicated classification and must not be confused with historical
evidence or active metadata.

### Active and requiring normalization

- `improvements/workflow.md` uses former service names in current workflow guidance.
- `improvements/improvements.json` uses former names in active metadata fields such as
  owners, affected repositories, and next-action text.
- The current workspace confirms that the repository identities are `pf-svc-income` and
  `pf-svc-reference` under `modules/`; the former repository names are not current
  checkout names. Historical Cloud Run resource names are infrastructure evidence and
  are outside this repository-metadata change.

`improvements/improvements.json` must be handled according to its generation contract;
it must not be hand-edited if the validator regenerates it from another source.

## Replacement policy

Apply the complete mapping in the brief, preserving the destination spelling exactly,
only to active, non-historical text. The compact forms are legacy aliases, not current
identities; the destination spelling is defined explicitly in the mapping table.

Before changing any file, classify each match as active metadata, current guidance,
stable identifier, historical evidence, or task-definition self-reference. Preserve
stable identifiers and historical evidence even when they contain a former alias. Treat
aliases as case-insensitive substrings for discovery, including compound names and URLs;
review each compound occurrence before replacing it.

## Risks

- Rewriting a historical record would damage auditability.
- Editing generated JSON directly could be overwritten or create drift.
- Renaming slugs or paths would break durable links.
- Treating a full-tree non-zero result as a failure without classifying historical
  findings would conflict with the explicit historical-evidence exception.

## Evidence required

- Case-insensitive inventory before and after the change.
- Validator output showing generated artifacts remain deterministic.
- Diff proving that only active guidance/metadata changed.
