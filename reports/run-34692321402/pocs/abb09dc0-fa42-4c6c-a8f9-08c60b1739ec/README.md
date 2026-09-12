# Offline PoC — abb09dc0-fa42-4c6c-a8f9-08c60b1739ec

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `transaction-manager/src/services/run-telemetry.service.test.ts:59`
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
