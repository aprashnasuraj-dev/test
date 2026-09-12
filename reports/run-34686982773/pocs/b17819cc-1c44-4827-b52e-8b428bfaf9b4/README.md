# Offline PoC — b17819cc-1c44-4827-b52e-8b428bfaf9b4

- Severity: **Medium**
- Asset: `transaction-manager`
- Rule: `detect-secrets:Secret Keyword`
- Source: `transaction-manager/src/helpers/getSmartAccountAddress.test.ts:23`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
