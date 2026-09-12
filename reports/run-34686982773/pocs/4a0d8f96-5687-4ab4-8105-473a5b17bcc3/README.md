# Offline PoC — 4a0d8f96-5687-4ab4-8105-473a5b17bcc3

- Severity: **Medium**
- Asset: `manager`
- Rule: `ui-message-origin-check`
- Source: `manager/src/features/notifications/utils/telegram/auth.ts:117`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
