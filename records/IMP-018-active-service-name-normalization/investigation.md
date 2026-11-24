# Investigation: active service-name normalization

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: `pf/improvements` active metadata and workflow guidance.

## Finding

The IMP-017 artifact directory contains no occurrences of the requested legacy aliases.
The broader improvements repository contains two classes of occurrences:

### Historical and permitted

Occurrences in `records/HIST-*` and completed improvement records document former
repositories, resources, migrations, or historical implementation state. They are
retained as evidence and must not be rewritten by this task.

Record names and stable slugs may also preserve former terminology because changing
them would break links and artifact history.

### Active and requiring normalization

- `improvements/workflow.md` uses former service names in current workflow guidance.
- `improvements/improvements.json` uses former names in active metadata fields such as
  owners, affected repositories, and next-action text.

`improvements/improvements.json` must be handled according to its generation contract;
it must not be hand-edited if the validator regenerates it from another source.

## Replacement policy

Apply the requested case-preserving replacements only to active, non-historical text.
The compact aliases are not identity operations: income and reference compact forms must
be replaced with their approved current identities.

Before changing any file, classify each match as active metadata, current guidance,
stable identifier, or historical evidence. Preserve stable identifiers and historical
evidence even when they contain a former alias.

## Risks

- Rewriting a historical record would damage auditability.
- Editing generated JSON directly could be overwritten or create drift.
- Renaming slugs or paths would break durable links.

## Evidence required

- Case-insensitive inventory before and after the change.
- Validator output showing generated artifacts remain deterministic.
- Diff proving that only active guidance/metadata changed.
