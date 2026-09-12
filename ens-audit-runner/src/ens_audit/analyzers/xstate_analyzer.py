"""Static XState state-machine analysis for transaction-manager sources."""

from __future__ import annotations

import re
from pathlib import Path

import networkx as nx

from ens_audit.models import Asset, Finding, Location, Severity

_SUBSCRIBE = re.compile(r"\.subscribe\s*\(\s*\{(?P<body>.*?)\}\s*\)", re.DOTALL)
_KEY = re.compile(r"^(?P<indent>\s*)(?P<name>[A-Za-z_$][\w$]*)\s*:\s*\{")
_TARGET = re.compile(r"target\s*:\s*['\"](?P<target>[^'\"]+)['\"]")
_INITIAL = re.compile(r"initial\s*:\s*['\"](?P<state>[^'\"]+)['\"]")


class XStateAnalyzer:
    """Analyze XState subscriptions and a conservative state-transition graph.

    Security invariant: state machine files are parsed as text only and never imported or
    executed.
    """

    def analyze(self, asset: Asset) -> list[Finding]:
        """Analyze transaction-machine source files for liveness and graph defects."""

        findings: list[Finding] = []
        for path in self._files(asset.path):
            text = path.read_text(encoding="utf-8", errors="replace")
            findings.extend(self._subscription_findings(asset, path, text))
            findings.extend(self._graph_findings(asset, path, text))
        return findings

    @staticmethod
    def _files(root: Path) -> list[Path]:
        """Return machine TypeScript files, preferring the documented ``src/machines`` tree."""

        machine_root = root / "src" / "machines"
        search_root = machine_root if machine_root.is_dir() else root
        return sorted(
            path
            for path in search_root.rglob("*.ts")
            if not path.is_symlink() and "node_modules" not in path.parts
        )

    @staticmethod
    def _subscription_findings(asset: Asset, path: Path, text: str) -> list[Finding]:
        """Flag object subscriptions that define ``next`` without a completion handler."""

        findings: list[Finding] = []
        for match in _SUBSCRIBE.finditer(text):
            body = match.group("body")
            if re.search(r"\bnext\s*:", body) and not re.search(r"\bcomplete\s*:", body):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(
                    Finding(
                        title="XState actor subscription handles next but not completion",
                        severity=Severity.HIGH,
                        asset=asset.name,
                        stage="sast",
                        rule_id="ens-xstate-missing-complete",
                        root_cause="xstate_subscription_missing_completion",
                        location=Location(file=str(path.relative_to(asset.path)), line=line),
                        description="Stopping the subscribed actor can leave an awaiting caller unsettled when no completion handler exists.",
                        evidence=match.group(0)[:4000],
                        confidence=0.9,
                    )
                )
        return findings

    def _graph_findings(self, asset: Asset, path: Path, text: str) -> list[Finding]:
        """Build a conservative directed state graph and report unreachable/unknown targets."""

        graph, initial, line_by_state, unknown_targets = self._extract_graph(text)
        findings: list[Finding] = []
        relative = str(path.relative_to(asset.path))
        for source, target, line in unknown_targets:
            findings.append(
                Finding(
                    title=f"State transition targets undefined state: {target}",
                    severity=Severity.MEDIUM,
                    asset=asset.name,
                    stage="sast",
                    rule_id="custom-xstate:undefined-target",
                    root_cause="xstate_dead_transition",
                    location=Location(file=relative, line=line, function=source),
                    description="A parsed machine transition targets a state not defined in the same states block.",
                    evidence=f"{source} -> {target}",
                    confidence=0.6,
                )
            )
        if initial and initial in graph:
            reachable = nx.descendants(graph, initial) | {initial}
            for state in sorted(set(graph.nodes) - reachable):
                findings.append(
                    Finding(
                        title=f"XState state is unreachable from initial state: {state}",
                        severity=Severity.LOW,
                        asset=asset.name,
                        stage="sast",
                        rule_id="custom-xstate:unreachable-state",
                        root_cause="xstate_unreachable_state",
                        location=Location(file=relative, line=line_by_state.get(state, 0), function=state),
                        description="No parsed transition path reaches this state from the machine's initial state.",
                        evidence=f"initial={initial}; unreachable={state}",
                        confidence=0.55,
                    )
                )
        return findings

    @staticmethod
    def _extract_graph(
        text: str,
    ) -> tuple[nx.DiGraph[str], str | None, dict[str, int], list[tuple[str, str, int]]]:
        """Extract top-level state names and quoted targets from a ``states`` object."""

        lines = text.splitlines()
        graph: nx.DiGraph[str] = nx.DiGraph()
        initial_match = _INITIAL.search(text)
        initial = initial_match.group("state") if initial_match else None
        in_states = False
        states_indent: int | None = None
        child_indent: int | None = None
        current: str | None = None
        line_by_state: dict[str, int] = {}
        pending: list[tuple[str, str, int]] = []
        for number, line in enumerate(lines, start=1):
            if not in_states and re.search(r"\bstates\s*:\s*\{", line):
                in_states = True
                states_indent = len(line) - len(line.lstrip())
                continue
            if not in_states or states_indent is None:
                continue
            indent = len(line) - len(line.lstrip())
            if line.strip().startswith("}") and indent <= states_indent:
                break
            key = _KEY.match(line)
            if key:
                key_indent = len(key.group("indent"))
                if child_indent is None and key_indent > states_indent:
                    child_indent = key_indent
                if key_indent == child_indent:
                    current = key.group("name")
                    graph.add_node(current)
                    line_by_state[current] = number
                    continue
            if current:
                for target_match in _TARGET.finditer(line):
                    pending.append((current, target_match.group("target").lstrip(".#"), number))
        unknown: list[tuple[str, str, int]] = []
        for source, target, line_number in pending:
            if target in graph:
                graph.add_edge(source, target)
            else:
                unknown.append((source, target, line_number))
        return graph, initial, line_by_state, unknown
