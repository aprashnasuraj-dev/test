# Offline PoC — 4fa56abd-fff0-449a-b5e9-5973fc011c2a

- Severity: **Medium**
- Asset: `manager`
- Stage: `sast`
- Rule: `custom-llm:prompt-injection-surface`
- Source hint: `manager/worker-configuration.gen.d.ts:4848`
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
