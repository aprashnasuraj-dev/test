# Offline PoC — 372210da-9548-447d-8a54-641bb5a7dc4d

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source hint: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/profile/utils/transformRecords.ts:54`
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
