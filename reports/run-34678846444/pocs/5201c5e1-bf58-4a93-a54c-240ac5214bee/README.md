# Offline PoC — 5201c5e1-bf58-4a93-a54c-240ac5214bee

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-unvalidated-open-url`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/notifications/utils/telegram/auth.ts:48`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
