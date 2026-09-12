"""Source-only tests for TypeScript/JavaScript taint analysis."""

from __future__ import annotations

from pathlib import Path

from ens_audit.analyzers.ts_analyzer import TypeScriptAnalyzer
from ens_audit.models import Asset, Severity


def test_tainted_values_propagate_to_all_modeled_sinks(tmp_path: Path) -> None:
    """Direct browser/request sources and simple assignments reach modeled sensitive sinks.

    Security invariant: fixture source is read as text only and is never imported or executed.
    """

    source = tmp_path / "flow.ts"
    source.write_text(
        "\n".join(
            [
                "const supplied = request.url;",
                "let forwarded = supplied;",
                "fetch(forwarded);",
                "window.open(forwarded);",
                "channel.postMessage(forwarded, '*');",
                "const sender = request.from;",
                "signPayload(sender);",
            ]
        ),
        encoding="utf-8",
    )
    asset = Asset("manager", tmp_path, "a" * 40)

    findings = TypeScriptAnalyzer().analyze(asset)

    assert {finding.rule_id for finding in findings} == {
        "custom-ts:untrusted-network-url",
        "custom-ts:untrusted-navigation-url",
        "custom-ts:untrusted-postmessage-target",
        "custom-ts:request-from-to-signer",
    }
    assert {finding.severity for finding in findings} == {Severity.HIGH, Severity.MEDIUM}
    assert all(finding.location.file == "flow.ts" for finding in findings)


def test_direct_source_in_sink_is_tainted_without_assignment(tmp_path: Path) -> None:
    """A modeled source used directly in a sink is detected without variable propagation.

    Security invariant: detection relies only on source text patterns.
    """

    (tmp_path / "direct.js").write_text("axios.get(notification.url);\n", encoding="utf-8")
    asset = Asset("workers", tmp_path, "b" * 40)

    findings = TypeScriptAnalyzer().analyze(asset)

    assert len(findings) == 1
    assert findings[0].root_cause == "untrusted_url_to_network_sink"
    assert findings[0].location.line == 1


def test_clean_constants_do_not_produce_findings(tmp_path: Path) -> None:
    """Constant destinations and unrelated identifiers remain untainted.

    Security invariant: the analyzer must not report a sink solely because it exists.
    """

    (tmp_path / "safe.tsx").write_text(
        "const safe = 'https://example.invalid';\nfetch(safe);\nwindow.open('/local');\n",
        encoding="utf-8",
    )
    asset = Asset("portal", tmp_path, "c" * 40)

    assert TypeScriptAnalyzer().analyze(asset) == []
    assert TypeScriptAnalyzer._expression_tainted("safe + constant", set()) is False


def test_source_discovery_skips_node_modules_and_non_source_files(tmp_path: Path) -> None:
    """Source discovery includes supported extensions and excludes dependency/generated inputs.

    Security invariant: dependency-tree files cannot influence local source-analysis results.
    """

    (tmp_path / "a.mjs").write_text("export const x = 1;\n", encoding="utf-8")
    (tmp_path / "b.cjs").write_text("module.exports = 1;\n", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("fetch(request.url);\n", encoding="utf-8")
    dependency = tmp_path / "node_modules" / "pkg"
    dependency.mkdir(parents=True)
    (dependency / "bad.js").write_text("fetch(request.url);\n", encoding="utf-8")

    files = TypeScriptAnalyzer._source_files(tmp_path)

    assert {path.name for path in files} == {"a.mjs", "b.cjs"}
