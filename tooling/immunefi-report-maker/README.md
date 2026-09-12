# Immunefi Report Maker

`immunefi_report_maker.py` converts validated audit notes into an Immunefi-style Markdown report. It can either polish prose through the OpenAI Responses API or run in a deterministic local-only mode that performs no API calls.

## Install

```bash
cd tooling/immunefi-report-maker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Do not commit API keys. For AI polishing, provide credentials through the environment:

```bash
export OPENAI_API_KEY='...'
export OPENAI_MODEL='gpt-5.6-luna' # optional override
```

## Create an input template

```bash
immunefi-report-maker --write-example finding.json
```

Input fields:

```json
{
  "title": "Finding title",
  "impact_category": "Smart Contract - High",
  "raw_brief": "Short factual issue summary.",
  "raw_details": "Detailed execution path, state changes, and affected identifiers.",
  "raw_recommendation": "Minimal remediation tied to the observed root cause.",
  "poc_code": "function testFinding() public { /* ... */ }",
  "poc_language": "solidity",
  "references": ["https://github.com/org/repo/blob/commit/path/File.sol#L1-L20"]
}
```

## Generate a polished report

```bash
immunefi-report-maker \
  --input finding.json \
  --output reports/finding.md
```

## Deterministic local-only compilation

```bash
immunefi-report-maker \
  --input finding.json \
  --output reports/finding.md \
  --no-polish
```

This mode is useful in CI and when the raw notes have already been reviewed.

## Validate without generating

```bash
immunefi-report-maker --input finding.json --validate-only
```

## Pipeline usage

The CLI accepts JSON from stdin, which lets fuzzers and reproduction harnesses feed findings directly into the report compiler:

```bash
cat finding.json | immunefi-report-maker --input - --output reports/finding.md
```

## Guardrails

The polishing prompt is intentionally evidence-bound. It instructs the model not to invent exploitability, severity, affected versions, file paths, asset loss, prerequisites, or attacker capabilities. The impact category is supplied by the researcher and is not reclassified by the model.

Generated reports should still be reviewed against the active program scope, impact taxonomy, and reproduction evidence before submission.
