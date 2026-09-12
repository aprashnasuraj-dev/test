# Offline PoC — c3562ccb-a5eb-4e6e-b127-d8013fed7c46

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/service/v1SubgraphClient.ts:178`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
