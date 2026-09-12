# Offline PoC — 17e1171d-a723-482e-9054-3963786861af

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source hint: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/roles/hooks/useGrantRoles.ts:27`
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
