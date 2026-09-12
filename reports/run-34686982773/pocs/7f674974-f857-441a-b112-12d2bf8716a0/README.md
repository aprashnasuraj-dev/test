# Offline PoC — 7f674974-f857-441a-b112-12d2bf8716a0

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/services/v1-names/index.test.ts:37`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
