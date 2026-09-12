# Offline PoC — 18306c8b-caea-43ee-a6a8-56e57f24e82b

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source hint: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/service/buildAtomicMigrationBatches.test.ts:101`
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
