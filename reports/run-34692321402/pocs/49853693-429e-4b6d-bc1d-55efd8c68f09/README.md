# Offline PoC — 49853693-429e-4b6d-bc1d-55efd8c68f09

- Severity: **Medium**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source hint: `manager/src/lib/smart-account/SmartAccountContext.tsx:809`
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
