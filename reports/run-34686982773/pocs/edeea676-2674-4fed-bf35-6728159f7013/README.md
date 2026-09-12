# Offline PoC — edeea676-2674-4fed-bf35-6728159f7013

- Severity: **High**
- Asset: `workers`
- Rule: `rpc-dynamic-fetch-url`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:430`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
