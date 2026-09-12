# Offline PoC — e97d4695-5657-4628-8f6c-6826b6b55f09

- Severity: **Medium**
- Asset: `smart-account`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source hint: `smart-account//home/runner/ens-audit/repos/audit-comp-ens/packages/smart-account/src/providers/rhinestone/initialize-account.ts:363`
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
