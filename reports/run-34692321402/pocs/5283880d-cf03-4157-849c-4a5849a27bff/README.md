# Offline PoC — 5283880d-cf03-4157-849c-4a5849a27bff

- Severity: **Medium**
- Asset: `manager`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `manager/worker-configuration.gen.d.ts:4670`
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
