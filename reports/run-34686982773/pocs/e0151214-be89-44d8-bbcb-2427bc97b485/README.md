# Offline PoC — e0151214-be89-44d8-bbcb-2427bc97b485

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `transaction-manager/src/services/run-telemetry.service.test.ts:59`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
