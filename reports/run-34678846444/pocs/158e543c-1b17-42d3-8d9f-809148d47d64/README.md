# Offline PoC — 158e543c-1b17-42d3-8d9f-809148d47d64

- Severity: **Medium**
- Asset: `workers`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-webhook-fail-open`
- Source: `workers//home/runner/ens-audit/repos/audit-comp-ens/workers/api-worker/worker-configuration.gen.d.ts:42`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
