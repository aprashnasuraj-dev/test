"""Source-only tests for LLM prompt-injection surface analysis."""

from __future__ import annotations

from pathlib import Path

from ens_audit.analyzers.prompt_injection import PromptInjectionAnalyzer
from ens_audit.models import Asset, Severity


def test_untrusted_prompt_construction_near_llm_call_is_reported(tmp_path: Path) -> None:
    """Untrusted application content interpolated into prompt construction is reported.

    Security invariant: fixture code is read as text only and is never sent to an LLM.
    """

    (tmp_path / "llm.ts").write_text(
        "const userInput = request.body;\n"
        "const messages = [{ role: 'user', content: `Review ${userInput}` }];\n"
        "await openai.chat.completions.create({ messages });\n",
        encoding="utf-8",
    )

    findings = PromptInjectionAnalyzer().analyze(Asset("manager", tmp_path, "a" * 40))

    assert len(findings) == 1
    assert findings[0].rule_id == "custom-llm:prompt-injection-surface"
    assert findings[0].severity is Severity.MEDIUM
    assert findings[0].location.file == "llm.ts"
    assert findings[0].location.line == 3


def test_explicit_untrusted_data_delimiter_suppresses_surface(tmp_path: Path) -> None:
    """An explicit untrusted-data delimiter in bounded context prevents the heuristic finding.

    Security invariant: explicit separation is recognized from source text, never executed.
    """

    (tmp_path / "guarded.ts").write_text(
        "const notes = request.body;\n"
        "const prompt = `<untrusted_notes>${notes}</untrusted_notes>`;\n"
        "await responses.create({ prompt });\n",
        encoding="utf-8",
    )

    assert PromptInjectionAnalyzer().analyze(Asset("manager", tmp_path, "b" * 40)) == []


def test_sanitizer_or_json_stringify_suppresses_surface(tmp_path: Path) -> None:
    """Nearby sanitizer/serialization signals prevent the conservative prompt finding.

    Security invariant: sanitizer recognition only suppresses the heuristic within local context.
    """

    (tmp_path / "safe.py").write_text(
        "notes = request.body\n"
        "prompt = sanitize(notes)\n"
        "anthropic.messages.create(prompt=prompt)\n",
        encoding="utf-8",
    )
    (tmp_path / "safe.ts").write_text(
        "const content = request.body;\n"
        "const messages = JSON.stringify(content);\n"
        "messages.create({ messages });\n",
        encoding="utf-8",
    )

    assert PromptInjectionAnalyzer().analyze(Asset("workers", tmp_path, "c" * 40)) == []


def test_llm_call_without_untrusted_prompt_context_is_ignored(tmp_path: Path) -> None:
    """A fixed prompt or unrelated LLM reference does not produce a prompt-injection finding.

    Security invariant: LLM API presence alone is insufficient for a security report.
    """

    (tmp_path / "fixed.js").write_text(
        "const prompt = 'Summarize the static release notes';\n"
        "openai.responses.create({ prompt });\n",
        encoding="utf-8",
    )
    (tmp_path / "not_call.ts").write_text("const description = request.body;\n", encoding="utf-8")

    assert PromptInjectionAnalyzer().analyze(Asset("portal", tmp_path, "d" * 40)) == []


def test_context_window_excludes_old_untrusted_construction(tmp_path: Path) -> None:
    """Untrusted prompt text more than thirty lines before the LLM call is not associated.

    Security invariant: the heuristic uses a bounded context window to avoid broad false positives.
    """

    lines = ["const userInput = request.body;", "const prompt = userInput;"]
    lines.extend(f"const filler{i} = {i};" for i in range(31))
    lines.append("openai.responses.create({ prompt: 'fixed' });")
    (tmp_path / "window.ts").write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert PromptInjectionAnalyzer().analyze(Asset("manager", tmp_path, "e" * 40)) == []


def test_file_discovery_includes_python_and_skips_node_modules(tmp_path: Path) -> None:
    """Discovery includes supported Python/JS variants and excludes dependency trees.

    Security invariant: third-party dependency source cannot create findings for the local asset.
    """

    (tmp_path / "local.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "local.jsx").write_text("const x = 1;\n", encoding="utf-8")
    dependency = tmp_path / "node_modules" / "pkg"
    dependency.mkdir(parents=True)
    (dependency / "bad.js").write_text(
        "const notes=request.body; const prompt=notes; openai.responses.create({prompt});\n",
        encoding="utf-8",
    )

    files = PromptInjectionAnalyzer._files(tmp_path)

    assert {path.name for path in files} == {"local.py", "local.jsx"}
