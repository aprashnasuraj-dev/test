# Offline PoC — 0257d89b-acb3-4627-a4ae-aa0becb60e54

- Severity: **High**
- Asset: `manager`
- Stage: `rpc`
- Rule: `rpc-dynamic-fetch-url`
- Source hint: `manager/src/features/profile/service/profileImageUpload.ts:150`
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
