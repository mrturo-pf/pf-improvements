# Recommendation: normalize active service names

Date: 2026-11-24  
Status: proposed  
Level: M  
Scope: active improvement metadata and workflow documentation.

## Recommendation

Proceed with a narrow terminology cleanup in the improvements repository. Update active
workflow instructions and the source of active improvement metadata to use the current
service identities. Validate and, where required, rename active files and directories as
well as their contents. Do not rewrite historical records, stable paths, slugs, or links.

The change should be implemented at the metadata source rather than by manually editing
`improvements/improvements.json` when that file is generated. Regenerate and validate the
catalog after the source update.

## Rationale

This preserves the historical record while preventing current contributors and agents
from copying obsolete service identities into new operational work. It also avoids the
classic documentation foot-gun: changing an old fact and pretending history was always
neat. History is messy; that is why it is called history.

## Decision gate

Implementation is safe only after identifying the generator/source for the active JSON
catalog. If no source exists, document that fact and make the smallest validated change
permitted by the repository workflow.

## Validation tool

Use `scripts/check-service-name-remnants.py` for the final case-insensitive scan. It
checks every readable file's content and every path component, and exits non-zero when
it finds a legacy alias. This prevents a content-only cleanup from leaving an obsolete
filename behind.

## Rollback

Revert only the active guidance/metadata commit, including path renames. Do not restore
or alter historical artifact contents as part of rollback.
