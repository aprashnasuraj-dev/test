# CI scripts

| Script | Called from | Purpose |
|---|---|---|
| `verify-submissions.sh` | `analysis.yml` — after `Run analysis` | Fail the run if any Critical/High/Medium escaped finding lacks `submissions/<id>.md` or `pocs/<id>/`. |
| `stage-output.sh` | `analysis.yml` — `Stage output` step | Reorganize `out/` into a submission-ready tree and generate `MANIFEST.json`, `SUBMISSION-CHECKLIST.md`, and `README.md`. |

Both scripts are idempotent and safe to run locally:

```bash
OUT_DIR=./out GITHUB_WORKSPACE=$PWD bash .github/scripts/verify-submissions.sh
GITHUB_WORKSPACE=$PWD bash .github/scripts/stage-output.sh
```

`verify-submissions.sh` normalizes between `$GITHUB_WORKSPACE/out` and `ens-audit-runner/out`. `stage-output.sh` uses the same normalization before creating `staging/`.
