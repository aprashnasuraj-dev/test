# Offline PoC — 91c694dd-39f2-4ff8-b3a3-9d3e1aaa4482

- Severity: **Medium**
- Asset: `workers`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-webhook-fail-open`
- Source hint: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/worker-configuration.gen.d.ts:42`
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
