# Offline PoC — 32a84fd7-46fd-4fc1-bef9-75c591097bd8

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/services/notifications/email-verification-rate-limit.test.ts:83`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
