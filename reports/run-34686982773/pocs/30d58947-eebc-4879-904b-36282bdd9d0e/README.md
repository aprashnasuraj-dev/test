# Offline PoC — 30d58947-eebc-4879-904b-36282bdd9d0e

- Severity: **High**
- Asset: `explorer`
- Rule: `custom-ssrf:dynamic-url-sink`
- Source: `explorer/src/hooks/useFundWallet.ts:12`
- Matched public issue: `R2-04`
- Escape reason: `severity_escalation`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
