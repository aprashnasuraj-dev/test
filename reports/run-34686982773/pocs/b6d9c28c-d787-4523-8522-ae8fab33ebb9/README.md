# Offline PoC — b6d9c28c-d787-4523-8522-ae8fab33ebb9

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Secret Keyword`
- Source: `transaction-manager/src/machines/registration/registration.actors.test.ts:41`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
