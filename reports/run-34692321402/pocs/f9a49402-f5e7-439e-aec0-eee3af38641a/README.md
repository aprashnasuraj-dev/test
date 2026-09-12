# Offline PoC — f9a49402-f5e7-439e-aec0-eee3af38641a

- Severity: **Medium**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `manager/worker-configuration.gen.d.ts:13544`
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
