# Offline PoC — 17a9f6b8-7a8b-4917-bb24-87f9bff3eb02

- Severity: **High**
- Asset: `explorer`
- Stage: `sast`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source hint: `explorer/src/hooks/useFundWallet.ts:12`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It verifies the
normalized finding metadata and, when a concrete current source location exists,
reproduces that source trace against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
