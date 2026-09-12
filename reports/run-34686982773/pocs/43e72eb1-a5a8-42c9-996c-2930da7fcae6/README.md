# Offline PoC — 43e72eb1-a5a8-42c9-996c-2930da7fcae6

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/utils/backend-client.ts:132`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
