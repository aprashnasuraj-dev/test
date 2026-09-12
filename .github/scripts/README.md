# CI scripts

| Script | Called from | Purpose |
|---|---|---|
| `generate-pocs.sh` | `analysis.yml` — after `Run analysis` | Generate and execute one offline, non-destructive source-trace PoC for every Critical/High/Medium escaped finding. |
| `verify-submissions.sh` | `analysis.yml` — after `Generate offline PoCs` | Fail the run if any Critical/High/Medium escaped finding lacks its submission markdown or required runnable PoC files/log marker. |
| `stage-output.sh` | `analysis.yml` — `Stage output` step | Reorganize `out/` into a submission-ready tree and generate `MANIFEST.json`, `SUBMISSION-CHECKLIST.md`, and `README.md`. |

All scripts are idempotent and safe to run locally against an existing analysis output:

```bash
OUT_DIR=./out GITHUB_WORKSPACE=$PWD bash .github/scripts/generate-pocs.sh
OUT_DIR=./out GITHUB_WORKSPACE=$PWD bash .github/scripts/verify-submissions.sh
GITHUB_WORKSPACE=$PWD bash .github/scripts/stage-output.sh
```

`generate-pocs.sh` and `verify-submissions.sh` normalize between `$GITHUB_WORKSPACE/out` and `ens-audit-runner/out`. Generated PoCs never contact live targets; they only verify the recorded source trace against the pinned local audit checkout.
