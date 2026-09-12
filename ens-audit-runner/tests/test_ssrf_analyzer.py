"""Source-only tests for SSRF sink analysis."""

from __future__ import annotations

from pathlib import Path

from ens_audit.analyzers.ssrf_analyzer import SSRFAnalyzer
from ens_audit.models import Asset, Severity


def test_dynamic_url_sink_without_guard_is_reported(tmp_path: Path) -> None:
    """Dynamic URL-like values reaching outbound requests without validation are findings.

    Security invariant: fixture source is parsed as text only; no outbound request is issued.
    """

    (tmp_path / "worker.ts").write_text(
        "const avatarUrl = event.data.avatar;\nfetch(avatarUrl);\n",
        encoding="utf-8",
    )
    findings = SSRFAnalyzer().analyze(Asset("workers", tmp_path, "a" * 40))

    assert len(findings) == 1
    assert findings[0].rule_id == "custom-ssrf:dynamic-url-sink"
    assert findings[0].severity is Severity.HIGH
    assert findings[0].location.file == "worker.ts"
    assert findings[0].location.line == 2


def test_nearby_destination_validation_suppresses_sink(tmp_path: Path) -> None:
    """A nearby URL/host validation signal prevents the conservative SSRF finding.

    Security invariant: validation recognition is based on bounded source context only.
    """

    (tmp_path / "guarded.ts").write_text(
        "const parsed = new URL(targetUrl);\n"
        "if (!allowlist.has(parsed.hostname)) throw new Error('blocked');\n"
        "axios.get(targetUrl);\n",
        encoding="utf-8",
    )

    findings = SSRFAnalyzer().analyze(Asset("portal", tmp_path, "b" * 40))

    assert findings == []


def test_literal_and_non_url_variables_are_ignored(tmp_path: Path) -> None:
    """Literal endpoints and variables without URL-like names do not trigger SSRF findings.

    Security invariant: sink presence alone is insufficient for a security report.
    """

    (tmp_path / "safe.js").write_text(
        "fetch('https://example.invalid/api');\n"
        "const value = input;\n"
        "http.get(value);\n",
        encoding="utf-8",
    )

    findings = SSRFAnalyzer().analyze(Asset("manager", tmp_path, "c" * 40))

    assert findings == []


def test_template_literal_with_interpolation_is_treated_as_dynamic(tmp_path: Path) -> None:
    """Interpolated template literals remain dynamic even though they begin with a quote marker.

    Security invariant: interpolation cannot bypass the dynamic-destination check.
    """

    (tmp_path / "template.ts").write_text(
        "fetch(`${endpoint}/profile`);\n",
        encoding="utf-8",
    )

    findings = SSRFAnalyzer().analyze(Asset("workers", tmp_path, "d" * 40))

    assert len(findings) == 1
    assert findings[0].root_cause == "server_side_fetch_of_untrusted_avatar_url"


def test_validation_window_is_bounded_to_twelve_prior_lines(tmp_path: Path) -> None:
    """Validation too far from a sink does not suppress a later unrelated dynamic request.

    Security invariant: only a bounded local context can justify suppressing a sink finding.
    """

    lines = ["const parsed = new URL(oldUrl);"]
    lines.extend(f"const filler{i} = {i};" for i in range(13))
    lines.append("https.get(targetUrl);")
    (tmp_path / "window.ts").write_text("\n".join(lines) + "\n", encoding="utf-8")

    findings = SSRFAnalyzer().analyze(Asset("workers", tmp_path, "e" * 40))

    assert len(findings) == 1


def test_file_discovery_skips_node_modules_and_non_source_files(tmp_path: Path) -> None:
    """Source discovery excludes dependency trees and unrelated file types.

    Security invariant: third-party dependency source cannot create local audit findings here.
    """

    (tmp_path / "local.cjs").write_text("fetch(targetUrl);\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("fetch(targetUrl);\n", encoding="utf-8")
    dependency = tmp_path / "node_modules" / "pkg"
    dependency.mkdir(parents=True)
    (dependency / "bad.js").write_text("fetch(targetUrl);\n", encoding="utf-8")

    files = SSRFAnalyzer._files(tmp_path)

    assert [path.name for path in files] == ["local.cjs"]
