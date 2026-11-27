# Brief: shared repository service-name normalization

Date: 2026-11-27  
Status: in progress  
Level: L  
Scope: repository identities, workspace paths, shared tooling references, gateway references, and architecture metadata.  
Related artifacts: investigation.md · recommendation.md · plan.md

## Objective

Rename the remaining PF repositories that do not use the active `pf-svc-*` service
identity convention:

| Current repository | Proposed repository |
|---|---|
| `pf-common` | `pf-svc-common` |
| `pf-gateway-proxy` | `pf-svc-gateway-proxy` |

The change must update GitHub repository names, local checkout paths, remotes, workspace
metadata, ecosystem documentation, architecture sources and generated architecture
artifacts, while preserving runtime behavior and public HTTP contracts.

## Acceptance criteria

1. Both GitHub repositories are renamed or their canonical replacement repositories are
   established with redirect behavior documented.
2. Local checkouts use `modules/pf-svc-common` and `modules/pf-svc-gateway-proxy`.
3. All active repository references, links, remotes, workspace indexes and architecture
   sources use the proposed names.
4. Historical records retain old names where they describe historical state, but every
   retained occurrence is classified in evidence.
5. Gateway runtime identifiers, Cloud Run service names, package names and deployed URLs
   are changed only if explicitly approved as a separate compatibility decision.
6. All affected repository checks and architecture validation pass.
7. No secrets, credentials, production payloads or historical evidence are introduced or
   rewritten silently.

## Non-objectives

- No database schema or table rename.
- No API route, API Gateway path, Cloud Run resource, service-account, package/module, or
  deployed service rename unless separately approved.
- No blind replacement inside historical improvement records.
- No direct production deployment as part of this artifact.
