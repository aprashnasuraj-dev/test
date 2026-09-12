# Offline PoC — 3baf215f-6bbb-4d92-a296-b749f480fc83

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/profile/utils/validateAbi.ts:21`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
