# Offline PoC — 4107f242-541a-4a6e-8355-c22fc037e30d

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/forward-resolution/components/AddressResolution/networks.ts:45`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
