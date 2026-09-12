# ENS Audit Runner

ENS Audit Runner is a Windows-native PySide6 application for source-only analysis of the ENS Immunefi audit-competition scope. It downloads a pinned upstream revision, runs a bounded multi-stage security pipeline, filters only explicitly disclosed known root causes, stores resumable checkpoints in SQLite, and exports analyst-ready JSON/Markdown reports.

## Audit scope

The runner maps the five published competition assets to the checked-in ENS workspace:

| Logical asset | Repository path |
| --- | --- |
| Manager | `apps/manager` |
| Explorer | `apps/portal` |
| Workers | `workers` |
| Transaction manager | `packages/transaction-manager` |
| Smart account | `packages/smart-account` |

Pinned upstream repository: `https://github.com/immunefi-team/audit-comp-ens.git`

Active verified commit: `1c9b47f18fcddd2e864dfe385c4171061c9811ae`

The originally requested SHA `63772fd872af472ced58b009499355f3430c2a86` could not be resolved in that upstream repository on 2026-09-12, so the runner fails closed to the repository-owned verified lock revision rather than inventing a target.

## Pipeline

The canonical pipeline order is:

1. **SAST** — local ENS analyzers plus CodeQL, Semgrep, Slither, and Bandit when available.
2. **Symbolic** — bounded Mythril and Halmos execution for Solidity-bearing assets.
3. **Fuzz** — bounded Foundry invariants and Echidna for Solidity-bearing assets; TypeScript property fuzzing is used only when the target supplies a real property-test harness.
4. **Dependencies** — npm audit, Snyk, and pip-audit normalization when their required manifests/tools are available.
5. **Secrets** — TruffleHog and detect-secrets with secret values discarded before persistence.
6. **Known issue filter** — suppression requires matching asset, root cause, and a narrow structural matcher.
7. **Report** — aggregate JSON, Markdown, and one Immunefi-style Markdown file per open finding.

A failed analyzer is isolated by default and remains retryable. Strict mode propagates the failure immediately. Successful per-asset stages are checkpointed in SQLite for resume.

External analyzer execution is Windows-first but not Windows-only: the resolver prefers native binaries and transparently falls back to verified WSL executables with argv-only execution and Windows-to-WSL path conversion.

## Built-in analyzers

The runner includes source-only checks that still work when external tools are unavailable:

- TypeScript/JavaScript source-to-sink taint heuristics
- SSRF sink/destination-validation checks
- LLM prompt-injection surface checks
- XState reachability and missing-completion checks
- Solidity dangerous-primitive checks
- ENS-specific Semgrep rules
- CodeQL security-extended configuration

These are triage aids, not proof of exploitability. A scanner match must still be validated against control flow, deployment assumptions, and competition impact rules.

## Safety properties

- External tools are invoked with argv arrays and `shell=False`.
- Audited source trees are treated as read-only inputs.
- Repository checkout is verified against the pinned commit.
- GUI code preview rejects paths outside the audited checkout and symlink targets.
- Secret scanner output is sanitized in memory; detected secret values are not stored in SQLite or reports.
- Known-issue suppression never triggers from area similarity alone. Asset and root cause must match first.
- A bypass of a known fix, a materially different consequence, or a different root cause remains open.
- Scanner credentials entered in Settings are session-only and scrubbed after the audit worker exits.
- CodeQL is disabled for an audit session unless its terms-confirmation checkbox is selected.

## Quick start on Windows

From PowerShell in this directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install-windows.ps1
```

If you have reviewed and accepted the applicable GitHub CodeQL terms:

```powershell
.\install-windows.ps1 -AcceptCodeQLTerms
```

For the Linux-oriented analyzers, open Ubuntu/WSL2 and run:

```bash
chmod +x install-wsl.sh
./install-wsl.sh
```

Then launch the application:

```powershell
ens-audit-runner
```

or, from source:

```powershell
py -3.12 -m ens_audit
```

See [INSTALL.md](INSTALL.md) for prerequisites, WSL notes, packaging, and troubleshooting.

## Runtime data

Runner-owned state is stored under:

```text
~/ens-audit/
├── repos/        # pinned upstream checkout
├── results/      # raw/sanitized analyzer outputs and reports
├── audit.sqlite3 # stage checkpoints and normalized findings
└── ens-audit.log
```

The audit checkout itself is never used as an output directory.

## Reports

The report stage writes:

- `audit-report.json` — complete normalized report
- `audit-report.md` — severity-grouped human-readable report
- `immunefi/` — one Markdown submission draft per unsuppressed finding

Suppressed known issues remain visible in the application/registry for traceability but are not exported as new reward-eligible findings.

## Development

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run checks:

```bash
ruff check src tests
mypy --strict src/ens_audit
bandit -r src/ens_audit -ll
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
pip-audit
```

CI runs these gates on Python 3.11 and 3.12.

## Build the Windows executable

On Windows with development dependencies installed:

```powershell
pyinstaller --clean --noconfirm ens-audit-runner.spec
```

Expected output:

```text
dist\ENSAuditRunner.exe
```

Validate the packaged startup path without launching an audit:

```powershell
.\dist\ENSAuditRunner.exe --smoke-test
Get-Content "$env:LOCALAPPDATA\ens-audit\logs\startup.log"
```

A successful smoke test exits with code `0` after a two-second Qt event loop and writes `SMOKE_TEST_OK` to the startup log.

The EXE contains the GUI, known-issue registry, and local rule files. Large third-party scanners are intentionally external so they can be independently updated and verified.

## Important limitation

Component-level scanner coverage is not equivalent to complete system security coverage. For example, CodeQL and Semgrep may both report no injection finding while a wallet-signing flow still constructs the wrong chain or recipient through valid-looking application state. The runner therefore combines static tools, state-machine analysis, property testing, known-issue comparison, and manual triage rather than treating any single tool as authoritative.
