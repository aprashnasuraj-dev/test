# Offline PoC — e1a457bd-e60f-46eb-851d-e1da0333e067

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/registry/hooks/useRevokeRegistryRoles.ts:26`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
