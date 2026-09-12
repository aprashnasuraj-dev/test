# Offline PoC — 70c332d5-b2c8-4198-9b13-458fedf01430

- Severity: **Medium**
- Asset: `manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `manager/src/features/notifications/notifications/name-transferred.tsx:6`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
