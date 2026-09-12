# Offline PoC — ae3ced90-03fc-4363-b7db-4bd4f5eb38ee

- Severity: **High**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
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
