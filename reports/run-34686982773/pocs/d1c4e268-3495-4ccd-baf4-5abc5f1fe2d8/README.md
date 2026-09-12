# Offline PoC — d1c4e268-3495-4ccd-baf4-5abc5f1fe2d8

- Severity: **Medium**
- Asset: `workers`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `workers/api-worker/worker-configuration.gen.d.ts:13543`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
