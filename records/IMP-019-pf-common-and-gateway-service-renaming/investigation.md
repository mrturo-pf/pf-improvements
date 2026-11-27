# Investigation: shared repository service-name normalization

Date: 2026-11-27  
Status: completed  
Level: L  
Scope: PF workspace repository identities and active references.

## Finding

The workspace currently contains these clean, independently tracked repositories:

| Local path | Remote | Proposed path | Role |
|---|---|---|---|
| `modules/pf-common` | `github.com/mrturo-pf/pf-common.git` | `modules/pf-svc-common` | shared Make targets and infrastructure helpers |
| `modules/pf-gateway-proxy` | `github.com/mrturo-pf/pf-gateway-proxy.git` | `modules/pf-svc-gateway-proxy` | scale-to-zero routing facade |

Both repositories are on `main`, aligned with `origin/main`, and currently have clean
working trees. The root workspace map, local AGENTS guidance, architecture sources, and
generated diagrams contain the current names. The gateway repository also uses its name
in README text, Python project metadata, and the FastAPI title/health response.

## Reference surfaces to audit during implementation

- GitHub repository names and redirects.
- Local directory names and each repository's `origin` URL.
- Root `AGENTS.md`, `README.md`, `modules/INDEX.json`, workspace scripts and workspace
  metadata.
- `architecture/base.json`, `architecture/index.html`, `architecture/README.md`, and
  generated HTML artifacts.
- Shared Makefile includes and consumer documentation in `pf-svc-income`,
  `pf-svc-reference`, and `pf-sheets`.
- Gateway README, `pyproject.toml`, package metadata, FastAPI title/health response,
  container/deployment configuration, OpenAPI configuration, CI and release workflows.
- Improvement records: classify historical references before changing them.

## Compatibility risk

The repository name, Python distribution name, import package name, Cloud Run service name,
API Gateway backend address, and human-facing service label are different namespaces.
They must not be renamed through one blind global replacement. In particular,
`pf_gateway_proxy` is an import/package identifier and may remain unchanged even if the
repository becomes `pf-svc-gateway-proxy`; changing it would be a separate code/API
migration.

Likewise, `pf-common` is a repository/tooling identity, while shared Make targets may be
referenced through relative paths or downloaded repository URLs. Every consumer must be
identified before changing the path.

## Evidence boundaries

Historical improvement records and old deployment evidence may retain the former names
when they describe the former repository or deployed resource. Active maps, links,
remotes, and current architecture metadata must use the proposed names after migration.
The implementation must produce before/after inventories and a classified residual list.
