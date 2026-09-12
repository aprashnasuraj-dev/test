# Offline PoC — 64317867-39df-4b61-8e08-94008a42e871

- Severity: **Medium**
- Asset: `workers`
- Stage: `ui`
- Rule: `ui-message-origin-check`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:4669`
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
