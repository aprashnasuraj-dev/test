# Offline PoC — d875ca07-d846-4934-8278-333fdb5a0107

- Severity: **Medium**
- Asset: `manager`
- Rule: `ui-message-origin-check`
- Source: `manager/src/features/notifications/utils/telegram/auth.ts:76`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
