# Offline PoC — b5779e64-9ea4-4fd5-846a-bbf70e2819f1

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-ssrf-untrusted-url`
- Source hint: `manager//home/runner/ens-audit/repos/audit-comp-ens/apps/manager/src/features/migration/service/v1SubgraphClient.ts:178`
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
