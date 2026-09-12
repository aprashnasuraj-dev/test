# Offline PoC — 9ad8e48f-5c77-421b-8ea5-8de33a876c07

- Severity: **High**
- Asset: `explorer`
- Rule: `rpc-dynamic-fetch-url`
- Source: `explorer/worker-configuration.d.ts:1841`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
