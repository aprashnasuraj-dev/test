# Offline PoC — 694d56ff-b3dc-49c0-85b5-70b9fec0e5e9

- Severity: **High**
- Asset: `manager`
- Rule: `rpc-dynamic-fetch-url`
- Source: `manager/src/features/profile/service/profileImageUpload.ts:150`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
