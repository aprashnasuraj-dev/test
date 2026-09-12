# Offline PoC — 55e45839-cb97-444e-b257-ca3e02332fa1

- Severity: **Medium**
- Asset: `workers`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source hint: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/services/sendgrid/contacts.ts:231`
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
