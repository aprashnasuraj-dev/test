# Offline PoC — 980c5e77-0e0b-40ee-b28c-4ae12cce9610

- Severity: **High**
- Asset: `workers`
- Rule: `rpc-dynamic-fetch-url`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:334`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
