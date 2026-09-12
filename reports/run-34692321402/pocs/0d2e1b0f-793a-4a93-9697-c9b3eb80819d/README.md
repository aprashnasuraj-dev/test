# Offline PoC — 0d2e1b0f-793a-4a93-9697-c9b3eb80819d

- Severity: **Medium**
- Asset: `explorer`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `explorer/src/features/forward-resolution/components/AddressResolution/AddressResolutionTable.tsx:11`
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
