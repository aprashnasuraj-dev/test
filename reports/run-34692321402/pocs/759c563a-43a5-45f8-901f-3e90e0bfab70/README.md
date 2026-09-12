# Offline PoC — 759c563a-43a5-45f8-901f-3e90e0bfab70

- Severity: **Medium**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:11914`
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
