"""Source-only tests for conservative Solidity primitive analysis."""

from __future__ import annotations

from pathlib import Path

from ens_audit.analyzers.solidity_analyzer import SolidityAnalyzer
from ens_audit.models import Asset, Severity


def test_all_sensitive_primitives_are_normalized(tmp_path: Path) -> None:
    """Each fixed Solidity primitive rule emits the expected normalized finding.

    Security invariant: the Solidity fixture is read as inert text and never compiled or executed.
    """

    (tmp_path / "Risky.sol").write_text(
        "contract Risky {\n"
        "function a(address target, bytes memory data) external { target.delegatecall(data); }\n"
        "function b() external view returns (address) { return tx.origin; }\n"
        "function c(address payable receiver) external { selfdestruct(receiver); }\n"
        "function d(address target) external { target.call{value: 1}(\"\"); }\n"
        "}\n",
        encoding="utf-8",
    )
    findings = SolidityAnalyzer().analyze(
        Asset("smart-account", tmp_path, "a" * 40, has_solidity=True)
    )

    assert [finding.rule_id for finding in findings] == [
        "solidity-delegatecall",
        "solidity-tx-origin",
        "solidity-selfdestruct",
        "solidity-low-level-call",
    ]
    assert [finding.severity for finding in findings] == [
        Severity.HIGH,
        Severity.MEDIUM,
        Severity.HIGH,
        Severity.MEDIUM,
    ]
    assert [finding.location.line for finding in findings] == [2, 3, 4, 5]
    assert all(finding.location.file == "Risky.sol" for finding in findings)


def test_comments_and_safe_contracts_do_not_produce_findings(tmp_path: Path) -> None:
    """Comment-only primitive names and ordinary typed calls remain clean.

    Security invariant: comments cannot create false-positive security reports.
    """

    (tmp_path / "Safe.sol").write_text(
        "// target.delegatecall(data); tx.origin; selfdestruct(receiver); target.call{value: 1}(\"\");\n"
        "contract Safe { function ping() external pure returns (uint256) { return 1; } }\n",
        encoding="utf-8",
    )

    assert SolidityAnalyzer().analyze(
        Asset("smart-account", tmp_path, "b" * 40, has_solidity=True)
    ) == []


def test_non_solidity_files_are_not_scanned(tmp_path: Path) -> None:
    """Files outside the Solidity suffix are ignored even if they contain matching text.

    Security invariant: analyzer scope is limited to explicit `.sol` source files.
    """

    (tmp_path / "Risky.txt").write_text("target.delegatecall(data);\n", encoding="utf-8")

    assert SolidityAnalyzer().analyze(
        Asset("smart-account", tmp_path, "c" * 40, has_solidity=True)
    ) == []
