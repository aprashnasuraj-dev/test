"""RPC/API trust-boundary analyzer for every configured audit asset."""

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
    confidence: float = 0.72


_RPC_MARKER = re.compile(
    r"\b(?:jsonrpc|rpc|provider\.request|wallet_|eth_|personal_|net_|web3_|"
    r"viem|ethers|JsonRpcProvider|request\(\s*\{\s*method)",
    re.IGNORECASE,
)

_RULES = (
    _Rule(
        "rpc-dynamic-method",
        re.compile(
            r"(?:provider\.)?request\s*\(\s*\{\s*method\s*:\s*(?![\"'`])",
            re.IGNORECASE | re.DOTALL,
        ),
        "RPC method name is dynamically selected",
        Severity.HIGH,
        "dynamic_rpc_method_without_local_allowlist",
        "An RPC request method is selected from a dynamic expression at the provider boundary.",
        "If request-controlled values reach this boundary, callers may invoke methods outside the intended capability set.",
        "Map untrusted input to a closed allowlist of RPC method constants before calling the provider.",
        "CWE-749",
        0.8,
    ),
    _Rule(
        "rpc-dynamic-fetch-url",
        re.compile(
            r"\bfetch\s*\(\s*(?![\"'`])(?:req(?:uest)?|body|input|params|query|url|endpoint)\b",
            re.IGNORECASE,
        ),
        "Request-derived value is used as an outbound fetch target",
        Severity.HIGH,
        "request_controlled_rpc_upstream",
        "A request/input-derived variable appears to select an outbound network destination.",
        "An attacker may redirect a server-side RPC proxy toward unintended hosts or metadata/internal services.",
        "Resolve upstreams from a fixed allowlist and reject arbitrary schemes, hosts, ports, redirects, and credentials.",
        "CWE-918",
        0.75,
    ),
    _Rule(
        "rpc-dynamic-websocket-url",
        re.compile(r"\bnew\s+WebSocket\s*\(\s*(?![\"'`])", re.IGNORECASE),
        "Dynamic value selects a WebSocket endpoint",
        Severity.MEDIUM,
        "dynamic_websocket_endpoint",
        "A dynamic expression controls the WebSocket destination.",
        "Unvalidated endpoint control can cross trust boundaries or expose credentials/messages to an unintended peer.",
        "Resolve WebSocket endpoints from a strict allowlist and enforce wss:// where applicable.",
        "CWE-918",
        0.7,
    ),
    _Rule(
        "rpc-wildcard-cors",
        re.compile(
            r"(?:Access-Control-Allow-Origin[\"']?\s*[:=]\s*[\"']\*[\"']|"
            r"cors\s*\(\s*\{\s*origin\s*:\s*(?:true|[\"']\*[\"']))",
            re.IGNORECASE | re.DOTALL,
        ),
        "RPC-capable code permits wildcard cross-origin access",
        Severity.MEDIUM,
        "wildcard_rpc_cors",
        "RPC/API-capable source configures a wildcard or universally permissive browser origin policy.",
        "Browser origins outside the intended trust boundary may be able to invoke or read the endpoint.",
        "Restrict CORS to the exact production origins that require browser access and keep credentialed routes non-wildcard.",
        "CWE-942",
        0.74,
    ),
    _Rule(
        "rpc-unbounded-jsonrpc-body",
        re.compile(
            r"(?:req(?:uest)?\.(?:body|json)|body|payload)\s*"
            r"(?:as\s+[^;\n]+)?[,\)]",
            re.IGNORECASE,
        ),
        "Raw request payload reaches RPC-capable code",
        Severity.MEDIUM,
        "rpc_payload_boundary_requires_schema",
        "RPC-capable code uses a raw request/body payload at a call boundary. This requires method and parameter schema validation.",
        "Malformed or over-privileged JSON-RPC data may reach privileged provider operations if validation is incomplete.",
        "Validate JSON-RPC version, method allowlist, parameter count/types/ranges, chain context, and request size before dispatch.",
        "CWE-20",
        0.55,
    ),
)

_ALLOWLIST = re.compile(
    r"(?:allowedMethods|allowed_methods|methodAllowlist|method_allowlist|"
    r"supportedMethods|supported_methods|switch\s*\(\s*(?:method|request\.method)|"
    r"\b(?:method|request\.method)\s+in\s+)",
    re.IGNORECASE,
)


class RPCStage:
    """Review RPC dispatch, upstream selection, and browser/API trust boundaries."""

    async def run(self, asset: Asset) -> list[Finding]:
        """Analyze all source files in one asset and record coverage."""
        files = iter_source_files(asset)
        findings: list[Finding] = []
        rpc_files = 0

        for path in files:
            text = read_text(path)
            if not _RPC_MARKER.search(text):
                continue
            rpc_files += 1
            relative = relative_file(asset, path)
            has_allowlist = bool(_ALLOWLIST.search(text))

            for rule in _RULES:
                for match in rule.pattern.finditer(text):
                    if rule.rule_id == "rpc-dynamic-method" and has_allowlist:
                        confidence = min(rule.confidence, 0.58)
                        severity = Severity.MEDIUM
                    else:
                        confidence = rule.confidence
                        severity = rule.severity
                    findings.append(
                        Finding(
                            title=rule.title,
                            severity=severity,
                            asset=asset.name,
                            stage="rpc",
                            rule_id=rule.rule_id,
                            root_cause=rule.root_cause,
                            location=Location(relative, line_number(text, match.start())),
                            description=rule.description,
                            evidence=match.group(0).strip().replace("\n", " ")[:240],
                            impact=rule.impact,
                            recommendation=rule.recommendation,
                            cwe=rule.cwe,
                            confidence=confidence,
                        )
                    )

        write_coverage(
            asset,
            "rpc",
            files=files,
            hits=len(findings),
            extra={
                "rpc_candidate_files": rpc_files,
                "rules_evaluated": len(_RULES),
                "scope_files_scanned": len(files),
            },
        )
        return findings
