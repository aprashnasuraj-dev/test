# Reusable Security Audit Toolkit Architecture

> Preservation and reuse guide for the audit tooling developed in `aprashnasuraj-dev/test`.
>
> Goal: preserve the working audit engine as a reusable security-analysis framework and make it straightforward to adapt the same architecture to future repositories without accidentally carrying ENS-specific scope, rules, or known issues into unrelated audits.

## 1. Preservation baseline

Known-good repository snapshot:

- Repository: `aprashnasuraj-dev/test`
- Baseline commit: `9e8b28e99af219c4c6b6dc620556e1dc095d9ce5`
- Successful workflow run: `34692321402`
- Workflow: `.github/workflows/analysis.yml`
- Successful run result: `completed / success`
- Archive branch: `archive/ens-audit-toolkit-2026-09-13`

Treat that archive branch as an immutable reference implementation. Future audit work should branch or copy from it rather than rewriting the historical baseline.

## 2. What we built

The project is not just a collection of scanners. It is an audit orchestration system with five important layers:

1. **Target locking and scope control**
   - downloads a fixed repository revision;
   - maps logical audit assets to repository paths;
   - keeps audit output outside the target source tree;
   - fails closed when the configured source revision cannot be verified.

2. **Multi-stage analysis**
   - SAST;
   - symbolic execution;
   - fuzzing/property testing;
   - dependency analysis;
   - secret scanning;
   - UI/security-state analysis;
   - RPC/trust-boundary analysis;
   - differential/security-regression analysis.

3. **Finding normalization and persistence**
   - all tools map into one internal finding model;
   - per-stage/per-asset checkpoints are persisted in SQLite;
   - failed stages can be retried without discarding successful work;
   - duplicate findings are normalized before reporting.

4. **Known-issue filtering and submission preparation**
   - known issues are matched by narrow structural criteria rather than broad similarity;
   - new, escaped, suppressed, rejected, and informational findings are separated;
   - final findings are rendered into JSON and Markdown.

5. **Evidence, PoC, and delivery automation**
   - offline PoC packages are generated;
   - staged output is validated;
   - GitHub Actions artifacts are published;
   - optional `reports` branch publishing gives a durable audit-history trail.

## 3. Canonical pipeline

The current engine defines this order:

```text
sast
  -> symbolic
  -> fuzz
  -> deps
  -> secrets
  -> ui
  -> rpc
  -> diff
  -> known_filter
  -> report
```

The eight analysis stages run per configured asset. The known-issue filter then runs per asset, followed by one aggregate report stage.

Core implementation:

```text
ens-audit-runner/src/ens_audit/pipeline/orchestrator.py
```

The orchestrator is one of the most reusable pieces in the repository. It already provides:

- deterministic stage ordering;
- selected-stage execution;
- pause/resume/cancel control;
- strict vs non-strict execution;
- per-asset checkpoints;
- resume of previous runs;
- failed-stage retry;
- completeness enforcement so missing stages cannot masquerade as full coverage.

## 4. Reusable internal components

### 4.1 Orchestrator

```text
ens-audit-runner/src/ens_audit/pipeline/orchestrator.py
```

Keep and reuse wherever possible.

Responsibilities:

- stage scheduling;
- asset iteration;
- error isolation;
- strict mode;
- resume/retry;
- completeness checks;
- final report coordination.

### 4.2 Normalized finding model

```text
ens-audit-runner/src/ens_audit/models.py
```

Reuse the normalized `Finding`, `Location`, severity, asset, and report abstractions instead of letting every external tool define its own output contract.

### 4.3 Persistent checkpoint store

```text
ens-audit-runner/src/ens_audit/pipeline/store.py
```

Reusable benefits:

- stage completion tracking;
- per-run source commit binding;
- normalized finding persistence;
- restart/resume support;
- audit traceability.

### 4.4 Tool execution abstraction

```text
ens-audit-runner/src/ens_audit/tooling.py
```

Important reusable security property:

- tools are invoked as argv arrays;
- shell interpolation is avoided;
- execution can resolve native or WSL tools;
- timeouts are explicit;
- audited source paths remain controlled.

### 4.5 Repository downloader and scope validator

```text
ens-audit-runner/src/ens_audit/downloader/repo_downloader.py
```

Reuse the architecture, but replace the target repository, branch, commit, and asset mapping for every new audit.

### 4.6 Reporting

```text
ens-audit-runner/src/ens_audit/pipeline/stage_report.py
```

Reusable responsibilities:

- aggregate normalized findings;
- create JSON report;
- create human-readable Markdown;
- generate submission-style Markdown.

The exact submission schema may need adaptation for a different bug-bounty program.

### 4.7 Known-issue registry

```text
ens-audit-runner/src/ens_audit/known_issues/registry.py
ens-audit-runner/src/ens_audit/known_issues/known_issues.yaml
ens-audit-runner/src/ens_audit/pipeline/stage_known_filter.py
```

Reuse the matching engine.

Do **not** reuse `known_issues.yaml` blindly. It is target-specific evidence and must be replaced or rebuilt for each audit target.

## 5. Built-in analyzers

These run even when third-party tools are unavailable.

| Analyzer | File | Reuse value | Notes |
| --- | --- | --- | --- |
| TypeScript/JavaScript security heuristics | `analyzers/ts_analyzer.py` | High | General source-to-sink and risky-pattern triage |
| SSRF analyzer | `analyzers/ssrf_analyzer.py` | High | Useful for server-side fetch and URL trust boundaries |
| Prompt-injection analyzer | `analyzers/prompt_injection.py` | Medium/High | Useful where repositories process LLM/user-authored prompt content |
| XState analyzer | `analyzers/xstate_analyzer.py` | High for state-machine apps | Looks for reachability/completion/security-state issues |
| Solidity analyzer | `analyzers/solidity_analyzer.py` | High for EVM projects | Source-level dangerous primitive and contract-pattern checks |

These analyzers are **triage engines, not exploit proof**. Every scanner hit still requires source-path validation, attacker-control analysis, reachability, and impact review.

## 6. External analyzer toolkit

The final-audit installer lives at:

```text
.github/scripts/install-final-audit-tools.sh
```

Current tool inventory:

| Tool | Primary role | Applicable targets |
| --- | --- | --- |
| CodeQL | deep static/code-flow analysis | JS/TS and supported CodeQL languages |
| Semgrep | pattern/taint SAST and custom rules | broad multi-language repos |
| Slither | Solidity static analysis | EVM/Solidity |
| Bandit | Python security linting | Python |
| Mythril | Solidity symbolic analysis | EVM/Solidity |
| Halmos | symbolic/property analysis | Solidity/EVM |
| Foundry / Forge | tests, invariants, fuzzing | Solidity/EVM |
| Echidna | property fuzzing | Solidity/EVM |
| npm audit | dependency vulnerability analysis | Node/npm/pnpm/yarn projects |
| Snyk | dependency/security analysis | supported ecosystems, when token is available |
| pip-audit | Python dependency CVE analysis | Python |
| TruffleHog | secret discovery | general repositories |
| detect-secrets | secret discovery and entropy/pattern checks | general repositories |
| Z3 | SMT solver dependency | symbolic-analysis stages |
| Git | deterministic source checkout and diff basis | all repositories |

### External-tool rules worth preserving

- CodeQL must not be silently installed or enabled when its applicable terms have not been explicitly accepted.
- Snyk must not be treated as available without a real `SNYK_TOKEN`.
- Secret values must be sanitized before persistence or reporting.
- Tool versions/installers should be verifiable and explicit.
- Every tool gets an execution timeout.
- Expected non-zero "finding found" exit codes must be handled deliberately rather than interpreted as infrastructure failure.

## 7. Analysis stages and how to reuse them

### Stage 1 — SAST

```text
pipeline/stage_sast.py
```

Combines:

- local analyzers;
- CodeQL;
- Semgrep;
- Slither where Solidity exists;
- Bandit where Python exists.

Reusable: yes.

Target-specific work:

- replace target custom Semgrep rules;
- adjust root-cause mapping;
- adjust language configuration if the new repository is not primarily JS/TS/Solidity/Python.

### Stage 2 — Symbolic

```text
pipeline/stage_symbolic.py
```

Uses bounded symbolic execution where Solidity-bearing assets are present.

Reusable: yes for smart-contract audits.

Target-specific work:

- identify executable contract roots;
- confirm compiler/build compatibility;
- validate assumptions before treating symbolic reachability as exploitability.

### Stage 3 — Fuzz

```text
pipeline/stage_fuzz.py
```

Current deep settings:

```text
Foundry invariant fuzz runs: 500000
Echidna testLimit:          500000
Echidna seqLen:             500
Echidna shrinkLimit:        25000
Per-fuzzer timeout:         7200 seconds
```

Reusable: yes for contract/property-test targets.

Important rule:

Do not run fake TypeScript fuzzing just to claim coverage. The existing stage deliberately runs TypeScript property fuzzing only when the target provides a real property-test harness.

### Stage 4 — Dependencies

```text
pipeline/stage_deps.py
```

Current ecosystem support includes Node and Python dependency scanning.

Reusable: yes.

For future audits add adapters for ecosystems such as:

- Cargo/Rust;
- Go modules;
- Maven/Gradle;
- Ruby Bundler;
- Composer/PHP;
- .NET/NuGet;
- other project-specific package managers.

### Stage 5 — Secrets

```text
pipeline/stage_secrets.py
```

Uses TruffleHog and detect-secrets.

Reusable: very high.

Preserve this invariant:

> Secret scanner evidence may identify the file/type/location, but raw secret values must not be written to SQLite, reports, logs, or submission artifacts.

### Stage 6 — UI/security-state analysis

```text
pipeline/stage_ui.py
```

Reusable for browser/wallet/front-end applications, especially where security depends on:

- user confirmation;
- recipient/chain/account selection;
- navigation targets;
- OAuth/postMessage flows;
- transaction construction;
- persistent browser state;
- service workers;
- wallet/session lifecycle.

This stage should be adapted heavily for non-web targets.

### Stage 7 — RPC/trust-boundary analysis

```text
pipeline/stage_rpc.py
```

Useful for applications that consume or forward:

- JSON-RPC;
- provider requests;
- untrusted API payloads;
- blockchain RPC methods;
- remote transaction data.

Reusable where an RPC boundary exists. Disable or replace it when it does not.

### Stage 8 — Diff/security-regression analysis

```text
pipeline/stage_diff.py
```

Reusable for:

- audit competitions;
- remediation reviews;
- fork/upstream comparisons;
- regression hunting;
- "known fix was bypassed" analysis;
- changed authorization/trust logic.

For future work, configure the correct baseline and head commits instead of assuming ENS history.

### Stage 9 — Known-issue filter

```text
pipeline/stage_known_filter.py
```

Reusable engine, target-specific data.

A suppression should require narrow evidence such as:

```text
same asset/component
+ same root cause
+ structural match
```

Never suppress merely because a finding sounds similar to a previously disclosed issue.

### Stage 10 — Report

```text
pipeline/stage_report.py
```

Reusable output engine.

Adapt the report/submission format to the destination program while keeping the normalized internal finding schema stable.

## 8. Target-specific files that must be replaced for a new audit

The biggest future-audit mistake would be to copy the entire runner and forget that some parts are ENS-specific.

### Mandatory replacement/review

```text
ens-audit-runner/src/ens_audit/config.py
ens-audit-runner/src/ens_audit/rules/ens-custom.yaml
ens-audit-runner/src/ens_audit/known_issues/known_issues.yaml
.github/workflows/analysis.yml
```

For a new target, explicitly set:

- repository URL;
- branch/tag/commit;
- logical asset names;
- repository-relative asset paths;
- target languages;
- source-only vs deploy/fork requirements;
- competition/bounty scope;
- known disclosed bugs;
- target-specific security invariants;
- report schema;
- artifact retention policy.

### Usually reusable with small changes

```text
pipeline/orchestrator.py
pipeline/store.py
models.py
tooling.py
downloader/repo_downloader.py
pipeline/stage_deps.py
pipeline/stage_secrets.py
pipeline/stage_report.py
.github/scripts/stage-output.sh
.github/scripts/verify-submissions.sh
```

### Reuse only when applicable

```text
analyzers/xstate_analyzer.py
analyzers/solidity_analyzer.py
pipeline/stage_symbolic.py
pipeline/stage_fuzz.py
pipeline/stage_ui.py
pipeline/stage_rpc.py
```

## 9. GitHub Actions audit architecture

Current workflow:

```text
.github/workflows/analysis.yml
```

Important behaviors worth preserving:

- explicit workflow inputs;
- exact target repository check;
- exact configured asset-set check;
- stage-name validation;
- test the engine wiring before running the audit;
- syntax-check helper scripts;
- install and inventory external analyzers;
- strict final-audit mode;
- capture `analysis.log`;
- generate PoCs only after successful analysis;
- always stage output;
- validate staged submissions;
- upload one structured artifact;
- optionally publish to a `reports` branch;
- `cancel-in-progress: false` so a newer push does not destroy a long-running audit.

For future repositories, consider moving the reusable workflow logic to a generic workflow such as:

```text
.github/workflows/security-audit.yml
```

and loading target scope from a target profile instead of hardcoding one program.

## 10. Output packaging toolchain

### PoC generator

```text
.github/scripts/generate-pocs.sh
```

Creates offline evidence packages for actionable findings.

Reusable concept: yes.

Important distinction:

> A generated `POC_OK` only proves that the audit evidence can be reproduced by the verifier. It must not automatically be described as proof of real-world exploitability.

For high-value findings, add a behavioral PoC that demonstrates the violated security invariant.

### Staging

```text
.github/scripts/stage-output.sh
```

Creates the delivery tree and index/manifest/checklist structure.

### Submission validation

```text
.github/scripts/verify-submissions.sh
```

Fail closed when required report sections or PoC files are missing.

### Tool verification

```text
.github/scripts/verify-final-audit-tools.sh
```

Snapshots or strictly requires the analyzer toolchain depending on run mode.

## 11. Artifact contract

The current workflow preserves a structured audit package containing:

```text
INDEX.md
README.md
MANIFEST.json
SUBMISSION-CHECKLIST.md
findings/
runs/
submissions/
pocs/
insights/
```

This structure is highly reusable and should remain stable even when individual analyzers change.

Recommended future contract:

```text
AUDIT-ARTIFACT/
├── INDEX.md
├── README.md
├── MANIFEST.json
├── SUBMISSION-CHECKLIST.md
├── findings/
│   ├── findings_new.json
│   ├── findings_escaped.json
│   ├── findings_suppressed.json
│   ├── findings_informational.json
│   └── findings_rejected.json
├── runs/
│   ├── analysis.log
│   └── toolchain snapshot
├── submissions/
├── pocs/
└── insights/
```

## 12. Finding taxonomy to preserve

Future audit adapters should keep the same review buckets:

- **new** — no accepted known match;
- **escaped** — related to a known root cause but materially distinct or more severe;
- **suppressed** — proven known issue under the configured narrow matcher;
- **informational** — hardening/best-practice without security impact;
- **rejected / false positive** — not a valid security finding;
- **duplicate** — same root cause/attack path/impact as another canonical finding.

This separation is essential because raw scanner counts are not valid vulnerability counts.

## 13. Future-audit target profile

A strong next iteration is to move target-specific configuration into a profile directory.

Recommended architecture:

```text
audit-targets/
├── ens/
│   ├── target.yaml
│   ├── custom-rules.yaml
│   ├── known-issues.yaml
│   └── report-profile.yaml
├── project-b/
│   ├── target.yaml
│   ├── custom-rules.yaml
│   ├── known-issues.yaml
│   └── report-profile.yaml
└── project-c/
    └── ...
```

Suggested `target.yaml` model:

```yaml
name: project-b
repository: https://github.com/example/project-b.git
commit: <verified immutable SHA>
assets:
  - name: web
    path: apps/web
  - name: contracts
    path: contracts
languages:
  - typescript
  - solidity
stages:
  - sast
  - symbolic
  - fuzz
  - deps
  - secrets
  - ui
  - rpc
  - diff
strict_final_audit: true
```

The reusable engine should load this profile, validate it, and refuse to invent missing scope.

## 14. Recommended generic package split

Long-term, separate the framework from the ENS profile:

```text
audit-framework/
├── core/
│   ├── orchestrator.py
│   ├── store.py
│   ├── models.py
│   ├── tooling.py
│   └── downloader.py
├── stages/
│   ├── sast.py
│   ├── symbolic.py
│   ├── fuzz.py
│   ├── dependencies.py
│   ├── secrets.py
│   ├── ui.py
│   ├── rpc.py
│   └── diff.py
├── analyzers/
├── packaging/
└── target_profiles/
    └── ens/
```

This avoids modifying core engine code every time a new target is audited.

## 15. Security-engineering rules for future audits

Preserve these rules regardless of target:

1. **Pin the source.** Audit an immutable commit, not a moving branch.
2. **Verify scope.** Never infer an asset path silently.
3. **Keep target source read-only.** Write all outputs elsewhere.
4. **No shell interpolation.** Use argv-only tool execution.
5. **Bound every analyzer.** Set deterministic timeouts and resource limits.
6. **Record tool availability.** A skipped/missing analyzer must never look like successful coverage.
7. **Fail closed in final mode.** Required tools or stages missing = incomplete audit.
8. **Keep checkpoints.** Long audits must be resumable.
9. **Normalize evidence.** Do not let one scanner's schema dominate the report.
10. **Separate scanner evidence from exploit proof.** Tool output is a lead, not final impact proof.
11. **Deduplicate semantically.** Same bug from five analyzers is one finding.
12. **Treat known issues narrowly.** Similarity alone is not suppression.
13. **Protect secrets.** Never persist raw credentials found by scanners.
14. **Re-rate severity manually.** Scanner severity is advisory only.
15. **Preserve all review decisions.** No original finding should disappear without a recorded disposition.
16. **PoCs should be safe and reproducible.** Prefer local tests, mocks, forks, or isolated fixtures.
17. **Report actual limitations.** Do not claim coverage from a tool that did not run.
18. **Keep a successful baseline.** Archive a known-good engine snapshot before major architecture changes.

## 16. Reuse workflow for the next audit

When starting a new target:

```text
1. Branch from the archived known-good toolkit.
2. Create a new target profile.
3. Pin and verify the target commit.
4. Define exact assets and repository paths.
5. Replace target-specific custom rules.
6. Replace the known-issue registry.
7. Review which stages actually apply.
8. Add/adjust language-specific analyzers.
9. Run engine unit tests.
10. Snapshot toolchain availability.
11. Run non-strict audit once for integration diagnostics.
12. Fix tooling/configuration defects only.
13. Run strict final audit.
14. Validate per-asset/per-stage coverage.
15. Generate PoCs and staging package.
16. Manually triage findings for reachability, exploitability, duplication, known issues, and severity.
17. Produce the final human-reviewed report.
18. Archive the final commit, workflow run, artifact digest, and report.
```

## 17. Files that define the current toolkit

Core engine:

```text
ens-audit-runner/src/ens_audit/models.py
ens-audit-runner/src/ens_audit/tooling.py
ens-audit-runner/src/ens_audit/downloader/repo_downloader.py
ens-audit-runner/src/ens_audit/pipeline/orchestrator.py
ens-audit-runner/src/ens_audit/pipeline/store.py
```

Stages:

```text
ens-audit-runner/src/ens_audit/pipeline/stage_sast.py
ens-audit-runner/src/ens_audit/pipeline/stage_symbolic.py
ens-audit-runner/src/ens_audit/pipeline/stage_fuzz.py
ens-audit-runner/src/ens_audit/pipeline/stage_deps.py
ens-audit-runner/src/ens_audit/pipeline/stage_secrets.py
ens-audit-runner/src/ens_audit/pipeline/stage_ui.py
ens-audit-runner/src/ens_audit/pipeline/stage_rpc.py
ens-audit-runner/src/ens_audit/pipeline/stage_diff.py
ens-audit-runner/src/ens_audit/pipeline/stage_known_filter.py
ens-audit-runner/src/ens_audit/pipeline/stage_report.py
```

Built-in analyzers:

```text
ens-audit-runner/src/ens_audit/analyzers/ts_analyzer.py
ens-audit-runner/src/ens_audit/analyzers/ssrf_analyzer.py
ens-audit-runner/src/ens_audit/analyzers/prompt_injection.py
ens-audit-runner/src/ens_audit/analyzers/xstate_analyzer.py
ens-audit-runner/src/ens_audit/analyzers/solidity_analyzer.py
```

Target/profile data:

```text
ens-audit-runner/src/ens_audit/config.py
ens-audit-runner/src/ens_audit/rules/ens-custom.yaml
ens-audit-runner/src/ens_audit/rules/codeql-config.yml
ens-audit-runner/src/ens_audit/known_issues/known_issues.yaml
ens-audit-runner/src/ens_audit/known_issues/registry.py
```

CI, packaging, and delivery:

```text
.github/workflows/analysis.yml
.github/scripts/install-final-audit-tools.sh
.github/scripts/verify-final-audit-tools.sh
.github/scripts/generate-pocs.sh
.github/scripts/stage-output.sh
.github/scripts/verify-submissions.sh
```

Desktop/analyst GUI:

```text
ens-audit-runner/src/ens_audit/gui/main_window.py
ens-audit-runner/src/ens_audit/gui/dashboard.py
ens-audit-runner/src/ens_audit/gui/findings_view.py
ens-audit-runner/src/ens_audit/gui/pipeline_view.py
ens-audit-runner/src/ens_audit/gui/known_issues_view.py
ens-audit-runner/src/ens_audit/gui/report_view.py
ens-audit-runner/src/ens_audit/gui/settings_view.py
```

Install/distribution:

```text
ens-audit-runner/install-windows.ps1
ens-audit-runner/install-wsl.sh
ens-audit-runner/ens-audit-runner.spec
ens-audit-runner/INSTALL.md
ens-audit-runner/README.md
ens-audit-runner/pyproject.toml
ens-audit-runner/requirements.txt
```

## 18. Preservation checklist

Before changing the framework materially:

- [ ] keep `archive/ens-audit-toolkit-2026-09-13` untouched;
- [ ] preserve baseline commit `9e8b28e99af219c4c6b6dc620556e1dc095d9ce5`;
- [ ] preserve successful workflow run metadata for `34692321402`;
- [ ] preserve the successful artifact/report package externally if long-term GitHub artifact retention is insufficient;
- [ ] do not overwrite the ENS known-issue registry with another target's data;
- [ ] do not generalize target scope by weakening commit/asset validation;
- [ ] add new analyzers behind the normalized `AnalysisStage` interface;
- [ ] add tests for every new stage and every target-specific adapter;
- [ ] keep final-audit mode fail-closed;
- [ ] document every future tool/version change.

## 19. Architectural principle

The reusable asset is **the orchestration, normalization, evidence handling, checkpointing, filtering, and packaging architecture**.

The least reusable asset is **the target-specific interpretation layer**: scope, custom rules, known issues, contracts, state assumptions, trust boundaries, and bounty-report wording.

For future audits, keep the engine stable and replace the target profile. That gives us the benefits of the same mature tooling without pretending that one project's assumptions apply to another project.
