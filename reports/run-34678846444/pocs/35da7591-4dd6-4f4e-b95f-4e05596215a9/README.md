# Offline PoC — 35da7591-4dd6-4f4e-b95f-4e05596215a9

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/resolver/hooks/useDeployPermissionedResolver.ts:125`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
