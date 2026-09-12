# Offline PoC — 93555b4e-4535-479f-a716-412e379b3c47

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `transaction-manager/src/services/run-telemetry.service.test.ts:93`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
