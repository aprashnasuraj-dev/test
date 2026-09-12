$ErrorActionPreference = "Stop"
$Root = if ($args.Count -gt 0) { $args[0] } else { Join-Path $HOME "ens-audit/repos/audit-comp-ens" }
python (Join-Path $PSScriptRoot "verify.py") $Root
exit $LASTEXITCODE
