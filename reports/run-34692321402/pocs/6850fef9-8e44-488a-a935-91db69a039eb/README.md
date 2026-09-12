# Offline PoC — 6850fef9-8e44-488a-a935-91db69a039eb

- Severity: **Medium**
- Asset: `explorer`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `explorer/worker-configuration.d.ts:4641`
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
