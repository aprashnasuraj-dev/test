# Offline PoC — ec124452-b0d8-4240-b425-e3e0db0095c9

- Severity: **Medium**
- Asset: `workers`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:1681`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
