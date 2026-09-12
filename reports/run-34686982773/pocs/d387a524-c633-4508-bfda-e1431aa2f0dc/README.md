# Offline PoC — d387a524-c633-4508-bfda-e1431aa2f0dc

- Severity: **Medium**
- Asset: `explorer`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `explorer/src/worker/safe-fetch.ts:193`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
