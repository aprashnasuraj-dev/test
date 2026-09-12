# Offline PoC — b5b0a0b5-63b1-4169-b0fa-2712e3ee7d5d

- Severity: **Medium**
- Asset: `smart-account`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source hint: `smart-account//home/runner/ens-audit/repos/audit-comp-ens/packages/smart-account/src/providers/rhinestone/session.test.ts:95`
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
