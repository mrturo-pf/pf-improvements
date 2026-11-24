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
catalog. If the JSON is generated, edit its source and regenerate it. If it is not
generated, document that fact and edit it directly as the smallest validated change
permitted by the repository workflow.

## Validation tool

Use `scripts/check-service-name-remnants.py` for the final case-insensitive inventory. It
checks every readable file's content and every path component, and exits `1` when it
finds a legacy alias, `2` when its inventory is incomplete or execution fails, and `0`
when it finds none. A full-tree non-zero result is expected while permitted historical
evidence remains; the validator is an inventory and escalation tool, not an automatic
historical exception list. Each finding must be classified manually before closure so a
filename cannot escape review merely because its contents are clean. Matched output is
limited to alias names and locations, not complete source lines, to avoid copying
secrets into evidence.

## Rollback

Revert only the active guidance/metadata commit, including path renames. Do not restore
or alter historical artifact contents as part of rollback.
