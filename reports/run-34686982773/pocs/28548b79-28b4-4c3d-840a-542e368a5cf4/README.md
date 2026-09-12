# Offline PoC — 28548b79-28b4-4c3d-840a-542e368a5cf4

- Severity: **Medium**
- Asset: `workers`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `workers/api-worker/src/services/delivery/templates/telegram.ts:51`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
