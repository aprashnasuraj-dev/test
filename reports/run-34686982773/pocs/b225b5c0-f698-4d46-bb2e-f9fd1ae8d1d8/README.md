# Offline PoC — b225b5c0-f698-4d46-bb2e-f9fd1ae8d1d8

- Severity: **Medium**
- Asset: `workers`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:1942`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
