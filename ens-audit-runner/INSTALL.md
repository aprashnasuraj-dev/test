# ENS Audit Runner installation

This guide describes the supported Windows-first setup for the ENS Audit Runner and its optional Linux/WSL analyzer toolchain.

## 1. Base Windows prerequisites

Install these first:

- Windows 10 or Windows 11 x64
- Python 3.12 x64 with the Windows `py` launcher
- Git for Windows
- Node.js LTS with npm if you want JavaScript dependency analysis or Snyk
- Ubuntu on WSL2 if you want the Linux-oriented Solidity analyzers

Verify the base commands from PowerShell:

```powershell
py -3.12 --version
git --version
node --version
npm --version
wsl.exe --status
```

`node`/`npm` and WSL are optional for a minimal GUI/local-analyzer installation, but missing tools reduce pipeline coverage.

## 2. Install the Windows application and native scanners

Open PowerShell in `ens-audit-runner` and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install-windows.ps1
```

The script:

- installs the Python application from the checked-out source
- installs `pip-audit`, `detect-secrets`, and `bandit`
- installs the latest official TruffleHog Windows AMD64 release
- verifies a published SHA-256 digest when the GitHub release supplies one
- adds runner-managed scanner directories to the current/user PATH
- does not persist scanner API tokens

### CodeQL

CodeQL is not installed unless you explicitly pass:

```powershell
.\install-windows.ps1 -AcceptCodeQLTerms
```

Review the applicable GitHub CodeQL terms before using that switch. The installer resolves the latest official `github/codeql-cli-binaries` Windows release dynamically instead of pinning a stale download URL.

The GUI also has an **I confirm CodeQL usage terms are accepted** checkbox. If it is unchecked, CodeQL is disabled for that audit session while the rest of SAST continues.

To intentionally omit CodeQL or TruffleHog:

```powershell
.\install-windows.ps1 -SkipCodeQL
.\install-windows.ps1 -SkipTruffleHog
```

## 3. Install Linux/WSL analyzers

From Ubuntu/WSL2, enter the repository directory and run:

```bash
chmod +x install-wsl.sh
./install-wsl.sh
```

The WSL script installs or verifies:

- Semgrep
- Slither
- Bandit
- Halmos
- Foundry (`forge`)
- Echidna
- pip-audit
- detect-secrets
- Mythril when a supported Python 3.10 interpreter is already available

Mythril's current upstream PyPI guidance supports Python 3.7–3.10. The installer therefore does **not** force Mythril into an unsupported Python 3.12 environment. If `python3.10` is absent, Mythril is skipped with a precise follow-up command.

The Echidna installer resolves the latest official x86_64 Linux release from GitHub and verifies the published SHA-256 digest when available.

## 4. How Windows/WSL tool routing works

The desktop application uses a shared tool resolver:

1. Prefer a native Windows executable found on PATH.
2. If native lookup fails and WSL is available, run `wsl.exe -e which <tool>`.
3. If the tool exists inside WSL, execute it using `wsl.exe --cd <mapped-path> -e <tool> ...`.
4. Absolute Windows paths are mapped to `/mnt/<drive>/...` for WSL argv values.
5. No analyzer command is constructed as a shell command string; subprocesses use argv arrays with shell interpretation disabled.

Open **Settings → Detect Tools** to see the actual native path, WSL path, and active route for every configured analyzer.

The pinned repository checkout stays on the Windows filesystem under `~/ens-audit/repos/`; WSL analyzers read the same checkout through `/mnt/...` mappings.

## 5. Optional Snyk setup

Snyk is optional. The runner never downloads it implicitly through `npx`.

With Node/npm installed, Snyk's official npm installation command is:

```powershell
npm install -g snyk
```

or inside a Linux environment:

```bash
npm install -g snyk
```

For the audit application, you can paste a `SNYK_TOKEN` into **Settings**. It is placed only in the current analyzer process environment and is cleared when the audit worker exits. The runner does not write it to SQLite, QSettings, logs, or report files.

## 6. Optional Semgrep authentication

Public Semgrep rules run without an application token. If you need authenticated Semgrep behavior, paste `SEMGREP_APP_TOKEN` into **Settings**.

Like the Snyk token, it is session-only and is cleared when the worker exits. When a tool runs in WSL, the selected environment variable is forwarded using WSL's environment forwarding mechanism rather than command-line arguments.

## 7. Start the application

After setup, open a new PowerShell window so persisted PATH changes are visible, then run:

```powershell
ens-audit-runner
```

From a source checkout you can also run:

```powershell
py -3.12 -m ens_audit
```

The first full audit clones the pinned ENS upstream repository into:

```text
~/ens-audit/repos/audit-comp-ens
```

and verifies that the detached checkout equals:

```text
1c9b47f18fcddd2e864dfe385c4171061c9811ae
```

## 8. Build a Windows executable

Install development dependencies:

```powershell
py -3.12 -m pip install -e ".[dev]"
```

Build:

```powershell
pyinstaller --clean --noconfirm ens-audit-runner.spec
```

Expected output:

```text
dist\ENSAuditRunner.exe
```

The executable bundles application code, known-issue YAML, Semgrep rules, and the CodeQL configuration. Large third-party analyzers remain external so their versions can be independently updated and verified.

## 9. Troubleshooting

### A tool says Missing even after installation

Use **Settings → Detect Tools** again. The resolver caches discovery during a process, and the Detect Tools action clears that cache. If PATH was changed by an installer, restarting the application is also appropriate.

For WSL tools, verify directly:

```powershell
wsl.exe -e which semgrep
wsl.exe -e which forge
wsl.exe -e which echidna
```

### Mythril is missing

This is expected on WSL distributions that do not provide Python 3.10. Halmos and the local Solidity analyzer still run. If Mythril is needed, install a supported Python 3.10 interpreter in WSL, then:

```bash
pipx install --python python3.10 mythril
```

### CodeQL is installed but does not run

Check the CodeQL terms checkbox in **Settings**. The application intentionally makes CodeQL unavailable for that session until consent is confirmed.

### Snyk does not run

Verify:

```powershell
snyk --version
```

Then provide a valid `SNYK_TOKEN` in Settings or authenticate the CLI through Snyk's supported authentication flow.

### npm audit is skipped

This is deliberate when an asset has no local `package-lock.json` or `npm-shrinkwrap.json`. The ENS workspace is pnpm-based; the runner does not fabricate an npm lockfile just to make `npm audit` run. Snyk remains available when explicitly installed.

### TypeScript fast-check does not appear in Fuzz results

The pinned ENS source does not currently contain a fast-check property-test harness, and fast-check does not expose the generic command-line runner originally assumed by the prototype. The runner therefore does not execute an invented `npx fast-check` command. Foundry and Echidna remain the bounded fuzzing engines for Solidity-bearing scope.

### An analyzer fails but the audit continues

Non-strict mode isolates analyzer failures and leaves the failed stage retryable. Use **Pipeline → Retry Failed** after correcting the tool/setup issue. A failed stage is never checkpointed as successful.

### Where are results stored?

```text
~/ens-audit/results/
~/ens-audit/audit.sqlite3
```

Secret-scanner raw secret values are not written there. Only sanitized detector metadata, normalized finding data, and report outputs are persisted.
