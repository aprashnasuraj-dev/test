# Offline PoC — 38a80a7c-ba68-4ed2-9a8a-27a2d28c0aaa

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
