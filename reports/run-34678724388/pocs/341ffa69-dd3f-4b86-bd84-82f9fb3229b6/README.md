# Offline PoC — 341ffa69-dd3f-4b86-bd84-82f9fb3229b6

- Severity: **Medium**
- Asset: `manager`
- Rule: `custom-ts:untrusted-navigation-url`
- Source: `manager/public/push-sw.js:76`
- Matched public issue: `EXP-INPUT-009`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
