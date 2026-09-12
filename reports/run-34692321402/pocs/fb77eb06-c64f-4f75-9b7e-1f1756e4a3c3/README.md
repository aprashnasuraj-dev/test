# Offline PoC — fb77eb06-c64f-4f75-9b7e-1f1756e4a3c3

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `transaction-manager/src/services/run-telemetry.service.test.ts:93`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
