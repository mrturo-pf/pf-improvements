# PF Improvements

Central repository for PF ecosystem improvement investigations, decisions, plans,
and durable coordination artifacts.

## Sources of truth

- **GitHub Issues:** intake, coordination, dependencies, next actions, resolutions,
  and links to technical evidence.
- **GitHub Project:** current status, categorical priority, numeric queue rank,
  owners, affected repositories, blockers, and operational views.
- **This repository:** investigations, briefs, recommendations, plans, decisions,
  validation evidence, and generated agent context.
- **Service repositories:** implementation, API, schema, deployment, and runtime
  documentation owned by each service.

The repository intentionally does not store current task status, priority, or queue
rank as editable task state.

## Layout

Each improvement has one directory under `improvements/`:

```text
improvements/<ID>-<slug>/
├── investigation.md
├── brief.md
├── recommendation.md
└── plan.md
```

Some historical improvements legitimately contain only the artifacts that existed
in their source repository. Missing historical metadata is marked explicitly rather
than inferred.

## Validation and generated context

```bash
python3 scripts/validate-improvements.py --write-generated
python3 scripts/validate-improvements.py
```

Generated outputs live under `generated/` and are produced by GitHub Actions. Do
not edit them manually.

## Intake

Create a GitHub Issue using the `Ecosystem improvement` template, add it to the
`PF Ecosystem Improvements` Project, and create the applicable artifacts here after
authorization. Do not create a second Markdown intake register.

All content in this public repository must be sanitized. Never commit credentials,
tokens, connection strings, raw production payloads, personal data, health data,
salaries, payslips, or unsanitized operational evidence.
