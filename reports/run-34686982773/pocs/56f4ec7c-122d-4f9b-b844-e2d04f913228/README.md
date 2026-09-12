# Offline PoC — 56f4ec7c-122d-4f9b-b844-e2d04f913228

- Severity: **Medium**
- Asset: `manager`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/profile/service/profileImageUpload.ts:150`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
