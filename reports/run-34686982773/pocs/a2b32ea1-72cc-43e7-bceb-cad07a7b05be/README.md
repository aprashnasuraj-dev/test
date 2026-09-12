# Offline PoC — a2b32ea1-72cc-43e7-bceb-cad07a7b05be

- Severity: **High**
- Asset: `manager`
- Rule: `rpc-dynamic-fetch-url`
- Source: `manager/worker-configuration.gen.d.ts:313`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
