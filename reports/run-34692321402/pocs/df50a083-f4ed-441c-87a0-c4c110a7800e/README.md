# Offline PoC — df50a083-f4ed-441c-87a0-c4c110a7800e

- Severity: **Medium**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:1942`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
