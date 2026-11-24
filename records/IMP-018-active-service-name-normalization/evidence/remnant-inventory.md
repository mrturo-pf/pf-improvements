# IMP-018 remnant inventory

Status: pending owner authorization and implementation

This file stores the before/after output of
`scripts/check-service-name-remnants.py`. The full-tree scan is intentionally exhaustive
and may report historical evidence and the equivalence-table self-reference. Those
findings are classified manually; they are not silently excluded.

## Before

Not captured yet. Run from the `improvements` repository root before implementation:

```bash
python3 scripts/check-service-name-remnants.py \
  > records/IMP-018-active-service-name-normalization/evidence/remnants-before.txt \
  2>&1 || true
```

## After

Not captured yet. Run the same command after active content and path normalization:

```bash
python3 scripts/check-service-name-remnants.py \
  > records/IMP-018-active-service-name-normalization/evidence/remnants-after.txt \
  2>&1 || true
```

## Classification

The final inventory must explain every reported occurrence as one of:

- historical evidence;
- stable identifier or historical path;
- generated output;
- active metadata or current workflow guidance requiring normalization;
- task-definition self-reference in the approved equivalence table.

Compound names and URLs require manual review before replacement. The inventory must
also record path findings separately from content findings.
