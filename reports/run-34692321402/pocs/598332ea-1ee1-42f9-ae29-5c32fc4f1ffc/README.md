# Offline PoC — 598332ea-1ee1-42f9-ae29-5c32fc4f1ffc

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source hint: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/utils/blockExplorer/getBlockExplorerTxUrl.ts:9`
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
