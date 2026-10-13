# AGENTS.md — pf-improvements

This repository owns the PF ecosystem's improvement investigations, design records,
implementation plans, validation evidence, and generated agent context.

## Source-of-truth boundaries

- GitHub Project `PF Ecosystem Improvements` owns current status, categorical
  priority, numeric queue rank, blockers, and operational views.
- GitHub Issues own intake, coordination, dependencies, next actions, resolutions,
  and links to technical evidence.
- This repository owns durable investigations, briefs, recommendations, plans,
  decisions, and sanitized release evidence.
- Service repositories own code and service-specific API, schema, deployment, and
  runtime documentation.

Do not add current task status, priority, or queue rank to repository metadata.

## Safety

- Never commit credentials, tokens, connection strings, personal data, health data,
  salaries, payslips, raw production payloads, or unsanitized logs.
- Security, privacy, data-loss, production-safety, and credential findings require
  immediate escalation; an Issue never replaces incident response.
- Preserve stable IDs and artifact history. Do not delete or rewrite historical
  evidence without explicit authorization.

## Artifact layout

Use one directory per improvement:

```text
improvements/<ID>-<slug>/
├── investigation.md
├── brief.md
├── recommendation.md
└── plan.md
```

Only create applicable artifacts. A Level L change requires a plan. Historical
missing metadata must be marked as unknown, not inferred.

## Validation

Run:

```bash
python3 scripts/validate-improvements.py --write-generated
python3 scripts/validate-improvements.py
```

Keep generated files under `generated/` deterministic and never edit them manually.

## Language and style

Documentation and identifiers are English. Use concise Markdown, stable links, and
preserve the workflow gates in `workflow.md`.
