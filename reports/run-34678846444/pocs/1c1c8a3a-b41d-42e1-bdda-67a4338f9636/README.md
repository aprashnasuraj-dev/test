# Offline PoC — 1c1c8a3a-b41d-42e1-bdda-67a4338f9636

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
