# Offline PoC — a0a379f5-d104-41d2-b9cd-20f321b186ff

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-ts:untrusted-navigation-url`
- Source hint: `manager/public/push-sw.js:76`
- Matched public issue: `EXP-INPUT-009`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
