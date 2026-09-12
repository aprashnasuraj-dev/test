# Offline PoC — c21e488f-f1b3-4842-9921-6bdfa36f9594

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/commemorative-nft/config.ts:37`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
