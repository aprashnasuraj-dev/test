# Offline PoC — b8f63fa0-7b14-4b8e-81c7-46a5e1a6190d

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/service/v1SubgraphClient.test.ts:22`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
