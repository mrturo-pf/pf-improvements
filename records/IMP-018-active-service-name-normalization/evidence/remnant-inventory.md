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
The temporary file must be outside the repository so the redirect cannot be scanned:

```bash
tmp=$(mktemp)
python3 scripts/check-service-name-remnants.py \
  --exclude-path records/IMP-018-active-service-name-normalization/evidence \
  > "$tmp" 2>&1
status=$?
printf 'exit=%s\\n' "$status" >> "$tmp"
case "$status" in 0|1) ;; *) cat "$tmp"; rm -f "$tmp"; exit "$status" ;; esac
mv "$tmp" records/IMP-018-active-service-name-normalization/evidence/remnants-before.txt
```

## After

Not captured yet. Run the same temporary-file workflow after active content and path
normalization, changing the destination to `remnants-after.txt`:

```bash
tmp=$(mktemp)
python3 scripts/check-service-name-remnants.py \
  --exclude-path records/IMP-018-active-service-name-normalization/evidence \
  > "$tmp" 2>&1
status=$?
printf 'exit=%s\\n' "$status" >> "$tmp"
case "$status" in 0|1) ;; *) cat "$tmp"; rm -f "$tmp"; exit "$status" ;; esac
mv "$tmp" records/IMP-018-active-service-name-normalization/evidence/remnants-after.txt
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
