# Offline PoC — 982e4c79-34f4-4694-96c0-29f5155368d0

- Severity: **Medium**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `manager/worker-configuration.gen.d.ts:11915`
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
