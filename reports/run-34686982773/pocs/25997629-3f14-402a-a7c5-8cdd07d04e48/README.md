# Offline PoC — 25997629-3f14-402a-a7c5-8cdd07d04e48

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Secret Keyword`
- Source: `transaction-manager/src/actors/warp-transport.actor.test.ts:55`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
