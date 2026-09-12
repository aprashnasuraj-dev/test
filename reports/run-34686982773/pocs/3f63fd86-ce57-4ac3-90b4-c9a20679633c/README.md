# Offline PoC — 3f63fd86-ce57-4ac3-90b4-c9a20679633c

- Severity: **Medium**
- Asset: `smart-account`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `smart-account//home/runner/ens-audit/repos/audit-comp-ens/packages/smart-account/src/providers/rhinestone/initialize-account.ts:363`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
