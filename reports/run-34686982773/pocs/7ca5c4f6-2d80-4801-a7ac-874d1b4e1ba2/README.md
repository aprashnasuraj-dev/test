# Offline PoC — 7ca5c4f6-2d80-4801-a7ac-874d1b4e1ba2

- Severity: **Medium**
- Asset: `explorer`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `explorer/worker-configuration.d.ts:11886`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
