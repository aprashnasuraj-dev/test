# Offline PoC — 81ebcc7e-1350-436a-ab71-125071a83ff5

- Severity: **High**
- Asset: `workers`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `workers/api-worker/worker-configuration.gen.d.ts:430`
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
