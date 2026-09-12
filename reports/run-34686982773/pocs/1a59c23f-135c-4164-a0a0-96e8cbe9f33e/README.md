# Offline PoC — 1a59c23f-135c-4164-a0a0-96e8cbe9f33e

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/services/expiry-discovery/index.test.ts:19`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
