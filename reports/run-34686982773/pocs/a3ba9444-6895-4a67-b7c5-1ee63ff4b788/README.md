# Offline PoC — a3ba9444-6895-4a67-b7c5-1ee63ff4b788

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `transaction-manager/src/services/run-telemetry.service.test.ts:275`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
