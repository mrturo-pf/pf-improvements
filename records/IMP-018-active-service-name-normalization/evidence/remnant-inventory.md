# IMP-018 remnant inventory

Status: pending owner authorization and implementation

This file stores the before/after output of
`scripts/check-service-name-remnants.py`. The scan is intentionally exhaustive for
source content and paths, while this evidence directory is explicitly excluded after
its first capture so the inventory does not audit its own previous output. Historical
evidence and task-definition/evidence self-references are classified manually; they are
not silently treated as active remnants.

## Before

Not captured yet. Run from the `improvements` repository root before implementation.
The temporary file must be outside the repository so the redirect cannot be scanned.
Run this as a shell script or source the function; it returns rather than closing an
interactive shell:

```bash
capture_inventory() {
  destination=$1
  tmp=$(mktemp) || return 2
  python3 scripts/check-service-name-remnants.py \
    --exclude-path records/IMP-018-active-service-name-normalization/evidence \
    > "$tmp" 2>&1
  status=$?
  printf 'exit=%s\n' "$status" >> "$tmp"
  case "$status" in
    0|1) ;;
    *) cat "$tmp"; rm -f "$tmp"; return "$status" ;;
  esac
  mv "$tmp" "$destination" || { rm -f "$tmp"; return 2; }
}

capture_inventory \
  records/IMP-018-active-service-name-normalization/evidence/remnants-before.txt
```

## After

Run the required regeneration and validation commands first. Then run the same function
after active content and path normalization, changing the destination to
`remnants-after.txt`:

```bash
capture_inventory \
  records/IMP-018-active-service-name-normalization/evidence/remnants-after.txt
```

## Classification

The final inventory must explain every reported occurrence as one of:

- historical evidence;
- stable identifier or historical path;
- generated output;
- active metadata;
- current workflow guidance;
- task-definition and evidence self-reference in the approved equivalence table or
  versioned inventory output.

Compound names and URLs require manual review before replacement. The inventory must
also record path findings separately from content findings.

## Execution summary

- Before scan: checker exit `1`; 1,042 content findings; 16 path findings; 0 skipped.
- After scan: checker exit `1`; 1,005 content findings; 16 path findings; 0 skipped.
- The remaining findings are historical records, stable historical slugs/URLs, generated
  output derived from those records, or this task's definition/evidence self-reference.
- No aliases remain in the active workflow guidance or in the selected active manifest
  entries (`IMP-006`, `IMP-007`, `IMP-009`, `IMP-010`, `IMP-011`, `IMP-013`).
- The after scan was run only after manifest regeneration and validation.
