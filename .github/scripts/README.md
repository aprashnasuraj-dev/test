# CI scripts

| Script | Called from | Purpose |
|---|---|---|
| `install-final-audit-tools.sh` | `analysis.yml` — manual `final_audit=true` runs | Install the external audit toolchain used by SAST, symbolic, fuzz, dependency, and secret stages. CodeQL installation is blocked unless its terms were explicitly accepted for that run. |
| `verify-final-audit-tools.sh` | `analysis.yml` — before analysis | Write `out/runs/toolchain.json` and, in strict final-audit mode, fail if a required analyzer executable is missing. Snyk becomes required only when `require_snyk=true`. |
| `generate-pocs.sh` | `analysis.yml` — after `Run analysis` | Generate and execute one offline, non-destructive source-trace PoC for every Critical/High/Medium escaped finding. |
| `verify-submissions.sh` | `analysis.yml` — after `Generate offline PoCs` | Fail the run if any Critical/High/Medium escaped finding lacks its submission markdown or required runnable PoC files/log marker. |
| `stage-output.sh` | `analysis.yml` — `Stage output` step | Reorganize `out/` into a submission-ready tree and generate `MANIFEST.json`, `SUBMISSION-CHECKLIST.md`, and `README.md`. |

The normal push workflow remains lightweight. A final audit is intentionally manual: open **Actions → ENS Submission Analysis → Run workflow**, keep the configured repository/assets, set `final_audit=true`, and set `accept_codeql_terms=true` only after reviewing and accepting the CodeQL CLI terms. Set `require_snyk=true` only when the repository has a `SNYK_TOKEN` Actions secret available. Final mode installs the complete non-Snyk toolchain, verifies executable availability, and runs the existing pipeline with strict analyzer failure handling.

All output/verification scripts are idempotent and safe to run locally against an existing analysis output:

```bash
STRICT_TOOLCHAIN=0 GITHUB_WORKSPACE=$PWD bash .github/scripts/verify-final-audit-tools.sh
OUT_DIR=./out GITHUB_WORKSPACE=$PWD bash .github/scripts/generate-pocs.sh
OUT_DIR=./out GITHUB_WORKSPACE=$PWD bash .github/scripts/verify-submissions.sh
GITHUB_WORKSPACE=$PWD bash .github/scripts/stage-output.sh
```

`generate-pocs.sh` and `verify-submissions.sh` normalize between `$GITHUB_WORKSPACE/out` and `ens-audit-runner/out`. Generated PoCs never contact live targets; they only verify the recorded source trace against the pinned local audit checkout.
