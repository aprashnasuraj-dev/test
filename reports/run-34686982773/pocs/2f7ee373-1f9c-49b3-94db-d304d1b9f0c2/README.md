# Offline PoC — 2f7ee373-1f9c-49b3-94db-d304d1b9f0c2

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/app/routes/wallet/index.ts:275`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
