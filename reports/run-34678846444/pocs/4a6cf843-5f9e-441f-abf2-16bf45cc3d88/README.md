# Offline PoC — 4a6cf843-5f9e-441f-abf2-16bf45cc3d88

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-shell-true-or-interpolated-command`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/worker/og-render.ts:15`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
