# Offline PoC — f48d4ae5-df71-4e7d-aae1-589b7b888c9b

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-shell-true-or-interpolated-command`
- Source hint: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/worker/og-render.ts:15`
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
