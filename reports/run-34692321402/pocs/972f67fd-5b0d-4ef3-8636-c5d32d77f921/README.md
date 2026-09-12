# Offline PoC — 972f67fd-5b0d-4ef3-8636-c5d32d77f921

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-json-parse-without-schema`
- Source hint: `explorer//home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/hooks/useSmartSessions.test.ts:35`
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
