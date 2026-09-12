# Offline PoC — 8f3a1a60-7cf0-40c4-b668-e1acb4887e73

- Severity: **High**
- Asset: `explorer`
- Rule: `rpc-dynamic-fetch-url`
- Source: `explorer/worker-configuration.d.ts:306`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
