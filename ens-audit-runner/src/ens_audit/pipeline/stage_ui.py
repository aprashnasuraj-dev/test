"""UI trust-boundary analyzer for every configured audit asset."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ens_audit.models import Asset, Finding, Location, Severity
from ens_audit.pipeline.scan_utils import (
    iter_source_files,
    line_number,
    read_text,
    relative_file,
    write_coverage,
)


@dataclass(frozen=True, slots=True)
class _Rule:
    rule_id: str
    pattern: re.Pattern[str]
    title: str
    severity: Severity
    root_cause: str
    description: str
    impact: str
    recommendation: str
    cwe: str | None = None


_RULES = (
    _Rule(
        "ui-dom-html-sink",
        re.compile(r"\.(?:innerHTML|outerHTML)\s*=\s*(?![\"'`])", re.I),
        "Dynamic HTML reaches a DOM parsing sink",
        Severity.HIGH,
        "untrusted_html_dom_sink",
        "A non-literal value is assigned to an HTML parsing property. If attacker-controlled data reaches this value, the browser may interpret markup or script.",
        "An attacker who controls the value may be able to execute script in the application's origin or alter trusted UI.",
        "Prefer textContent or a framework-safe renderer. If HTML is required, enforce a narrow allowlist sanitizer before the sink.",
        "CWE-79",
    ),
    _Rule(
        "ui-insert-adjacent-html",
        re.compile(r"\.insertAdjacentHTML\s*\(\s*[^,]+,\s*(?![\"'`])", re.I),
        "Dynamic markup reaches insertAdjacentHTML",
        Severity.HIGH,
        "untrusted_insert_adjacent_html",
        "Dynamic content is passed into insertAdjacentHTML, a browser HTML parsing sink.",
        "Controllable markup can become DOM XSS in the application's origin.",
        "Avoid HTML-string insertion or sanitize with a reviewed allowlist before insertion.",
        "CWE-79",
    ),
    _Rule(
        "ui-document-write",
        re.compile(r"\bdocument\.(?:write|writeln)\s*\(", re.I),
        "document.write is used in application UI code",
        Severity.MEDIUM,
        "document_write_sink",
        "document.write/writeln creates a direct HTML parsing boundary that is difficult to secure when data is dynamic.",
        "Unsafe data flow into this call can permit script execution or DOM replacement.",
        "Replace document.write with DOM APIs that keep data as text, or strictly sanitize any required HTML.",
        "CWE-79",
    ),
    _Rule(
        "ui-dynamic-code",
        re.compile(r"(?<![\w.])(?:eval\s*\(|new\s+Function\s*\()", re.I),
        "Dynamic JavaScript execution primitive is present",
        Severity.HIGH,
        "dynamic_code_execution_ui",
        "The source uses eval or Function construction, which turns data into executable JavaScript.",
        "If attacker-influenced input reaches the primitive, arbitrary script can execute in the page context.",
        "Remove dynamic code execution and use explicit parsing/dispatch instead.",
        "CWE-95",
    ),
    _Rule(
        "ui-react-dangerous-html",
        re.compile(r"dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:\s*(?![\"'`])", re.I),
        "Dynamic value reaches dangerouslySetInnerHTML",
        Severity.HIGH,
        "react_dangerous_html",
        "A dynamic expression is supplied to React's raw HTML rendering escape hatch.",
        "Untrusted content may become DOM XSS.",
        "Render structured React elements or sanitize through a reviewed allowlist immediately before this prop.",
        "CWE-79",
    ),
    _Rule(
        "ui-wildcard-postmessage",
        re.compile(r"\.postMessage\s*\([^,\n]+,\s*[\"']\*[\"']", re.I),
        "postMessage uses a wildcard target origin",
        Severity.MEDIUM,
        "wildcard_postmessage_target",
        "A message is sent with targetOrigin='*', so any navigated/embedded recipient can receive it.",
        "Sensitive cross-window data can be disclosed to an unintended origin.",
        "Use the exact expected scheme, host, and port as targetOrigin.",
        "CWE-346",
    ),
    _Rule(
        "ui-sensitive-web-storage",
        re.compile(
            r"(?:localStorage|sessionStorage)\.(?:setItem\s*\(\s*[\"'][^\"']*"
            r"(?:token|secret|private|mnemonic|seed|auth|session)[^\"']*[\"']|"
            r"(?:token|secret|privateKey|mnemonic|seed|auth|session)\s*=)",
            re.I,
        ),
        "Sensitive authentication material is written to Web Storage",
        Severity.MEDIUM,
        "sensitive_material_web_storage",
        "Authentication or key-like material appears to be persisted in localStorage/sessionStorage, which is readable by script in the origin.",
        "Any same-origin script compromise can expose reusable credentials or wallet material.",
        "Prefer HttpOnly/Secure/SameSite cookies for web sessions and avoid persistent browser storage for private key material.",
        "CWE-922",
    ),
)

_MESSAGE_LISTENER = re.compile(
    r"(?:addEventListener\s*\(\s*[\"']message[\"']|onmessage\s*=)", re.I
)


class UIStage:
    """Perform deterministic browser/UI sink and cross-origin boundary review."""

    async def run(self, asset: Asset) -> list[Finding]:
        """Analyze one complete asset and write explicit coverage evidence."""
        files = iter_source_files(asset)
        findings: list[Finding] = []
        ui_files = [
            path for path in files
            if path.suffix.lower() in {".cjs", ".html", ".htm", ".js", ".jsx", ".mjs", ".svelte", ".ts", ".tsx", ".vue"}
        ]

        for path in ui_files:
            text = read_text(path)
            relative = relative_file(asset, path)
            for rule in _RULES:
                for match in rule.pattern.finditer(text):
                    evidence = match.group(0).strip().replace("\n", " ")[:240]
                    findings.append(
                        Finding(
                            title=rule.title,
                            severity=rule.severity,
                            asset=asset.name,
                            stage="ui",
                            rule_id=rule.rule_id,
                            root_cause=rule.root_cause,
                            location=Location(relative, line_number(text, match.start())),
                            description=rule.description,
                            evidence=evidence,
                            impact=rule.impact,
                            recommendation=rule.recommendation,
                            cwe=rule.cwe,
                            confidence=0.78,
                        )
                    )

            for listener in _MESSAGE_LISTENER.finditer(text):
                window = text[listener.start(): listener.start() + 1800]
                if re.search(r"(?:event|evt|e)\.origin|origin\s*[!=]==?", window, re.I):
                    continue
                findings.append(
                    Finding(
                        title="Cross-window message handler lacks a nearby origin check",
                        severity=Severity.MEDIUM,
                        asset=asset.name,
                        stage="ui",
                        rule_id="ui-message-origin-check",
                        root_cause="missing_postmessage_origin_validation",
                        location=Location(relative, line_number(text, listener.start())),
                        description="A message event handler is registered without an origin comparison in the nearby handler body.",
                        evidence=listener.group(0).strip()[:240],
                        impact="A hostile window or frame may be able to send messages that the application treats as trusted.",
                        recommendation="Validate event.origin against an exact allowlist and validate the message schema before acting on event.data.",
                        cwe="CWE-346",
                        confidence=0.7,
                    )
                )

        write_coverage(
            asset,
            "ui",
            files=ui_files,
            hits=len(findings),
            extra={"candidate_files": len(ui_files), "rules_evaluated": len(_RULES) + 1},
        )
        return findings
