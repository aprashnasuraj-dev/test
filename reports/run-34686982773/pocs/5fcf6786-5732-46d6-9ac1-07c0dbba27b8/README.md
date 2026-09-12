# Offline PoC — 5fcf6786-5732-46d6-9ac1-07c0dbba27b8

- Severity: **Medium**
- Asset: `smart-account`
- Rule: `detect-secrets:Secret Keyword`
- Source: `smart-account/src/providers/rhinestone/initialize-account.test.ts:473`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
