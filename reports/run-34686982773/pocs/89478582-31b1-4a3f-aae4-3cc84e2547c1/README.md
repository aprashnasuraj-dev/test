# Offline PoC — 89478582-31b1-4a3f-aae4-3cc84e2547c1

- Severity: **Medium**
- Asset: `manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `manager/src/features/migration/service/decodeMigrationError.ts:260`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
