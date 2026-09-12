# Offline PoC — 89f76902-5a1d-4d2d-bd30-28ca1993fc2e

- Severity: **Medium**
- Asset: `explorer`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `explorer/src/features/roles/components/RoleHistoryTable.tsx:16`
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
