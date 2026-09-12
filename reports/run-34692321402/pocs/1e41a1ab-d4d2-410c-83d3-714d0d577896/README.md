# Offline PoC — 1e41a1ab-d4d2-410c-83d3-714d0d577896

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `transaction-manager/src/providers/transactionManager.ts:444`
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
