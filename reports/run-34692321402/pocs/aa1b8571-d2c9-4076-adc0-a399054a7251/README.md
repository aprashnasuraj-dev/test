# Offline PoC — aa1b8571-d2c9-4076-adc0-a399054a7251

- Severity: **Medium**
- Asset: `smart-account`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-unscoped-session-authority`
- Source hint: `smart-account//home/runner/ens-audit/repos/audit-comp-ens/packages/smart-account/src/providers/rhinestone/session.ts:85`
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
