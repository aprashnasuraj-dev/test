"""Source-only tests for XState subscription and graph analysis."""

from __future__ import annotations

from pathlib import Path

from ens_audit.analyzers.xstate_analyzer import XStateAnalyzer
from ens_audit.models import Asset, Severity


def test_missing_completion_subscription_is_reported(tmp_path: Path) -> None:
    """A subscription with `next` but no `complete` emits the known R3-02-class pattern.

    Security invariant: fixture TypeScript is parsed as text only and never imported or executed.
    """

    machine_root = tmp_path / "src" / "machines"
    machine_root.mkdir(parents=True)
    (machine_root / "subscription.ts").write_text(
        "actor.subscribe({ next: resolve });\n",
        encoding="utf-8",
    )

    findings = XStateAnalyzer().analyze(Asset("transaction-manager", tmp_path, "a" * 40))

    assert len(findings) == 1
    assert findings[0].rule_id == "ens-xstate-missing-complete"
    assert findings[0].severity is Severity.HIGH
    assert findings[0].location.file == "src/machines/subscription.ts"
    assert findings[0].location.line == 1


def test_completion_handler_prevents_subscription_finding(tmp_path: Path) -> None:
    """A subscription defining both `next` and `complete` is not reported.

    Security invariant: the analyzer must not broaden the known pattern beyond missing completion.
    """

    machine_root = tmp_path / "src" / "machines"
    machine_root.mkdir(parents=True)
    (machine_root / "safe.ts").write_text(
        "actor.subscribe({ next: resolve, complete: resolve });\n",
        encoding="utf-8",
    )

    assert XStateAnalyzer().analyze(
        Asset("transaction-manager", tmp_path, "b" * 40)
    ) == []


def test_graph_reports_undefined_target_and_unreachable_state(tmp_path: Path) -> None:
    """Undefined transition targets and states unreachable from `initial` are normalized.

    Security invariant: graph construction consumes only quoted state names and target text.
    """

    machine_root = tmp_path / "src" / "machines"
    machine_root.mkdir(parents=True)
    (machine_root / "flow.ts").write_text(
        "const machine = createMachine({\n"
        "  initial: 'idle',\n"
        "  states: {\n"
        "    idle: {\n"
        "      on: { START: { target: 'working' } },\n"
        "    },\n"
        "    working: {\n"
        "      on: { BAD: { target: 'missing' } },\n"
        "    },\n"
        "    orphan: {\n"
        "    },\n"
        "  },\n"
        "});\n",
        encoding="utf-8",
    )

    findings = XStateAnalyzer().analyze(Asset("transaction-manager", tmp_path, "c" * 40))
    by_rule = {finding.rule_id: finding for finding in findings}

    assert by_rule["custom-xstate:undefined-target"].location.function == "working"
    assert by_rule["custom-xstate:undefined-target"].evidence == "working -> missing"
    assert by_rule["custom-xstate:undefined-target"].location.file == "src/machines/flow.ts"
    assert by_rule["custom-xstate:unreachable-state"].location.function == "orphan"
    assert by_rule["custom-xstate:unreachable-state"].severity is Severity.LOW
    assert by_rule["custom-xstate:unreachable-state"].location.file == "src/machines/flow.ts"


def test_reachable_graph_has_no_graph_findings(tmp_path: Path) -> None:
    """A closed graph whose states are all reachable from `initial` remains clean.

    Security invariant: valid transitions do not create liveness findings solely by existing.
    """

    machine_root = tmp_path / "src" / "machines"
    machine_root.mkdir(parents=True)
    path = machine_root / "reachable.ts"
    path.write_text(
        "createMachine({\n"
        "  initial: 'idle',\n"
        "  states: {\n"
        "    idle: {\n"
        "      on: { START: { target: 'done' } },\n"
        "    },\n"
        "    done: {\n"
        "    },\n"
        "  },\n"
        "});\n",
        encoding="utf-8",
    )

    assert XStateAnalyzer()._graph_findings(
        Asset("transaction-manager", tmp_path, "d" * 40),
        path,
        path.read_text(encoding="utf-8"),
    ) == []


def test_machine_directory_is_preferred_when_present(tmp_path: Path) -> None:
    """Discovery limits itself to `src/machines` when that documented tree exists.

    Security invariant: unrelated TypeScript elsewhere in the asset cannot affect machine results.
    """

    machine_root = tmp_path / "src" / "machines"
    machine_root.mkdir(parents=True)
    (machine_root / "inside.ts").write_text("const x = 1;\n", encoding="utf-8")
    (tmp_path / "outside.ts").write_text(
        "actor.subscribe({ next: resolve });\n",
        encoding="utf-8",
    )

    files = XStateAnalyzer._files(tmp_path)

    assert [path.name for path in files] == ["inside.ts"]


def test_extract_graph_without_states_or_initial_is_empty() -> None:
    """Text without a machine states block yields an empty graph and no unknown transitions.

    Security invariant: malformed or unrelated source cannot fabricate graph nodes.
    """

    graph, initial, lines, unknown = XStateAnalyzer._extract_graph("const x = 1;\n")

    assert list(graph.nodes) == []
    assert initial is None
    assert lines == {}
    assert unknown == []
