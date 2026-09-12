# Offline PoC — cca13815-18de-4bac-9745-6a8a5b3cabe5

- Severity: **Medium**
- Asset: `workers`
- Stage: `sast`
- Rule: `custom-llm:prompt-injection-surface`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:4846`
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
