# Offline PoC — d9910d9a-48ab-42e6-a517-a763ca864757

- Severity: **Medium**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `workers/api-worker/src/services/delivery/templates/telegram.ts:28`
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
