# Offline PoC — b060a880-4740-4bf4-82a5-9ff3a73b266b

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/src/services/sendgrid/contacts.ts:61`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
