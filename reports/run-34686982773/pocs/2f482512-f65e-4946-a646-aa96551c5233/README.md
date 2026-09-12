# Offline PoC — 2f482512-f65e-4946-a646-aa96551c5233

- Severity: **High**
- Asset: `workers`
- Rule: `rpc-dynamic-fetch-url`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:1869`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
