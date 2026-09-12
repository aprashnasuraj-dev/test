# Offline PoC — 5952b120-e74a-40f4-9bca-415006acba0f

- Severity: **Medium**
- Asset: `workers`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `workers/api-worker/src/services/delivery/templates/telegram.ts:28`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
