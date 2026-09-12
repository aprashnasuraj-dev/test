# Offline PoC — f8f9ed91-56ff-4037-9745-3ed05115d3dd

- Severity: **Medium**
- Asset: `explorer`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/hooks/useFundWallet.ts:12`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
