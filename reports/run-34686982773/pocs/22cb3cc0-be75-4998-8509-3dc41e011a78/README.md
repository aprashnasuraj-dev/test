# Offline PoC — 22cb3cc0-be75-4998-8509-3dc41e011a78

- Severity: **Medium**
- Asset: `smart-account`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source: `smart-account//home/runner/ens-audit/repos/audit-comp-ens/packages/smart-account/src/providers/rhinestone/session-storage.ts:48`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
