# Offline PoC — 963fe60a-8909-4b3d-84d7-9042bce62fe8

- Severity: **Medium**
- Asset: `explorer`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `explorer/src/worker/avatar.test.ts:225`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
