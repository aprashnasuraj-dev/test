# Offline PoC — 0adc6545-d2dc-4b5f-943e-990ea0f0eea4

- Severity: **Medium**
- Asset: `manager`
- Rule: `rpc-unbounded-jsonrpc-body`
- Source: `manager/src/features/register-v2/workflow/pricing/components/TokenPickerContent.tsx:161`
- Matched public issue: `none`
- Escape reason: `none`

This PoC is intentionally offline and non-destructive. It reproduces the exact
source trace recorded by the analyzer against the pinned audit checkout.

## Run

```bash
bash run.sh /path/to/audit-comp-ens
```

A successful reproduction prints `POC_OK`.
