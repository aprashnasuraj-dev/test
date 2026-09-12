# Chain selection or fallback requires comparison with the connected wallet chain.

**Severity:** Medium
**Asset:** explorer
**Impact:** Impact requires reviewer confirmation from the supplied trace.

## Summary
Chain selection or fallback requires comparison with the connected wallet chain.

## Vulnerability Detail
Chain selection or fallback requires comparison with the connected wallet chain.

- Root cause: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Rule: `home.runner.work.test.test.ens-audit-runner.src.ens_audit.rules.ens-chainid-not-validated`
- Location: `/home/runner/ens-audit/repos/audit-comp-ens/apps/portal/src/features/resolver/hooks/useDeployPermissionedResolver.ts:125`

## Impact
Impact requires reviewer confirmation from the supplied trace.

## Proof of Concept
```text
Chain selection or fallback requires comparison with the connected wallet chain.
```

## Recommendation
Add a fail-closed validation at the identified trust boundary and add a regression test.

## References
- None recorded
