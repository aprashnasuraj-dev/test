# Offline PoC — d232e30d-95d7-4271-a07a-d0953b22fd0b

- Severity: **Medium**
- Asset: `manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `manager/src/features/migration/service/decodeMigrationError.ts:248`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
