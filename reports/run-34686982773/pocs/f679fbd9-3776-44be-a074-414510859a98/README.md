# Offline PoC — f679fbd9-3776-44be-a074-414510859a98

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `transaction-manager/src/providers/transactionManager.ts:444`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
