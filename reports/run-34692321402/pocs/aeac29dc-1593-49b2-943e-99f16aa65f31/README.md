# Offline PoC — aeac29dc-1593-49b2-943e-99f16aa65f31

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source hint: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/commemorative-nft/eligibility.test.ts:147`
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
