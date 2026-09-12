# Offline PoC — 1b57114b-9304-49cb-8ea6-d5de63de819d

- Severity: **Medium**
- Asset: `workers`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:13543`
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
