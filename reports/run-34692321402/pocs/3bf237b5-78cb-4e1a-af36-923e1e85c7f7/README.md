# Offline PoC — 3bf237b5-78cb-4e1a-af36-923e1e85c7f7

- Severity: **Medium**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `manager/src/features/notifications/notifications/name-transferred.tsx:6`
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
