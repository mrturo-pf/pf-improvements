# Recommendation: rename shared PF repositories

Date: 2026-11-27  
Status: in progress  
Level: L  
Scope: repository identity and active ecosystem references.

## Recommendation

Implementation is now in progress on coordinated branches. The GitHub repositories have
been renamed, local checkouts and active references are being migrated, and protected
`main` branches will receive the changes through pull requests.

Proceed with a staged repository-identity migration:

1. Rename `pf-common` to `pf-svc-common`.
2. Rename `pf-gateway-proxy` to `pf-svc-gateway-proxy`.
3. Update local checkout paths, remotes, workspace indexes, active documentation and
   architecture sources.
4. Regenerate derived indexes and architecture HTML from their sources.
5. Preserve runtime package/import identifiers and deployed resource names unless a
   separate compatibility decision authorizes those changes.

Execute the gateway repository rename before changing consumer references, and verify
GitHub redirects and branch protection. Keep the shared tooling repository's consumer
contract unchanged while only its repository identity moves.

## Rationale

The active service repositories already use the `pf-svc-*` convention. Leaving the shared
repository and gateway repository outside that convention makes workspace navigation,
architecture diagrams, automation and future service discovery inconsistent. A staged
identity-only migration limits risk: repository paths and links change, while HTTP routes,
Python imports, Cloud Run resources and database contracts remain stable.

## Decision gates

Implementation must not begin until the owner confirms:

- the exact target names `pf-svc-common` and `pf-svc-gateway-proxy`;
- whether GitHub repository rename redirects are acceptable;
- whether package/distribution names and Cloud Run service names remain unchanged;
- the consumer checkout migration window;
- the required PR/branch workflow in each repository.

## Rollback

Restore the previous local paths and `origin` URLs, and use GitHub rename redirects or
repository settings to restore the former canonical identity if the migration is stopped.
Do not roll back by rewriting Git history or deleting historical records.
