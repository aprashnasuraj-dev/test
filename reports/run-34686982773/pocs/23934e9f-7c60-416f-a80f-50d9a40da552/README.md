# Offline PoC — 23934e9f-7c60-416f-a80f-50d9a40da552

- Severity: **Medium**
- Asset: `explorer`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `explorer/src/worker/ens.test.ts:175`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
