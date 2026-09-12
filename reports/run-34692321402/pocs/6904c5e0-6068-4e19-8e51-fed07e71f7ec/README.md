# Offline PoC — 6904c5e0-6068-4e19-8e51-fed07e71f7ec

- Severity: **Medium**
- Asset: `explorer`
- Stage: `sast`
- Rule: `custom-llm:prompt-injection-surface`
- Source hint: `explorer/worker-configuration.d.ts:4819`
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
