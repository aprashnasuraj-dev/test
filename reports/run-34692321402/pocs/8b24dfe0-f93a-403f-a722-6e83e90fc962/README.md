# Offline PoC — 8b24dfe0-f93a-403f-a722-6e83e90fc962

- Severity: **High**
- Asset: `workers`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `workers/api-worker/src/services/delivery/push.ts:111`
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
