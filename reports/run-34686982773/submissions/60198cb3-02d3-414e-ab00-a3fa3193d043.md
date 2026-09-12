# Potential secret detected: Secret Keyword

**Severity:** Medium
**Asset:** transaction-manager
**Impact:** Impact requires reviewer confirmation from the supplied trace.

## Summary
detect-secrets identified credential-like material.

## Vulnerability Detail
detect-secrets identified credential-like material.

- Root cause: `committed_credentials`
- Rule: `detect-secrets:Secret Keyword`
- Location: `TRANSACTION_MANAGER_SPEC.md:618`

## Impact
Impact requires reviewer confirmation from the supplied trace.

## Proof of Concept
```text
detector=Secret Keyword
```

## Recommendation
Add a fail-closed validation at the identified trust boundary and add a regression test.

## References
- None recorded
