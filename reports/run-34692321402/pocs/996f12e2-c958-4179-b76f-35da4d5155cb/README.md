# Offline PoC — 996f12e2-c958-4179-b76f-35da4d5155cb

- Severity: **Medium**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `workers/api-worker/src/services/delivery/templates/telegram.ts:51`
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
