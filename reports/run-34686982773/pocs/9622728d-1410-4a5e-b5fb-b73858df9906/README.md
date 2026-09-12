# Offline PoC — 9622728d-1410-4a5e-b5fb-b73858df9906

- Severity: **Medium**
- Asset: `smart-account`
- Rule: `ui-sensitive-web-storage`
- Source: `smart-account/src/providers/rhinestone/session-storage.test.ts:62`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
