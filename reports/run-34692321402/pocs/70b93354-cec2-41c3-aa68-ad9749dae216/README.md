# Offline PoC — 70b93354-cec2-41c3-aa68-ad9749dae216

- Severity: **Medium**
- Asset: `transaction-manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-request-from-not-validated`
- Source hint: `transaction-manager//home/runner/ens-audit/repos/audit-comp-ens/packages/transaction-manager/src/actors/eoa-transport.actor.ts:40`
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
