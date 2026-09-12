# Offline PoC — 397ff392-d4e7-4369-a486-ad11c677692b

- Severity: **High**
- Asset: `explorer`
- Rule: `rpc-dynamic-fetch-url`
- Source: `explorer/worker-configuration.d.ts:496`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
