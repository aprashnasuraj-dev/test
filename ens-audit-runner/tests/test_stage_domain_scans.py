"""Focused coverage for UI, RPC, and diff security stages."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ens_audit.models import Asset, Severity
from ens_audit.pipeline import stage_diff
from ens_audit.pipeline.stage_diff import DiffStage
from ens_audit.pipeline.stage_rpc import RPCStage
from ens_audit.pipeline.stage_ui import UIStage


def _asset(tmp_path: Path, name: str = "manager") -> Asset:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return Asset(name, root, "b" * 40)


@pytest.mark.asyncio
async def test_ui_stage_scans_dom_and_message_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    asset = _asset(tmp_path)
    (asset.path / "ui.ts").write_text(
        "target.innerHTML = payload;\n"
        "window.addEventListener('message', event => consume(event.data));\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ens_audit.pipeline.scan_utils.RESULTS_DIR", tmp_path / "results")

    findings = await UIStage().run(asset)

    rule_ids = {finding.rule_id for finding in findings}
    assert "ui-dom-html-sink" in rule_ids
    assert "ui-message-origin-check" in rule_ids
    assert all(finding.asset == "manager" for finding in findings)
    coverage = json.loads(
        (tmp_path / "results/manager/ui/coverage.json").read_text(encoding="utf-8")
    )
    assert coverage["status"] == "completed"
    assert coverage["files_scanned"] == 1


@pytest.mark.asyncio
async def test_ui_stage_accepts_nearby_message_origin_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    asset = _asset(tmp_path)
    (asset.path / "safe.ts").write_text(
        "window.addEventListener('message', event => {\n"
        "  if (event.origin !== trustedOrigin) return;\n"
        "  consume(event.data);\n"
        "});\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ens_audit.pipeline.scan_utils.RESULTS_DIR", tmp_path / "results")

    findings = await UIStage().run(asset)

    assert "ui-message-origin-check" not in {finding.rule_id for finding in findings}


@pytest.mark.asyncio
async def test_rpc_stage_scans_dynamic_method_and_upstream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    asset = _asset(tmp_path, "workers")
    (asset.path / "rpc.ts").write_text(
        "provider.request({ method: request.method, params: request.body });\n"
        "fetch(request.url);\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ens_audit.pipeline.scan_utils.RESULTS_DIR", tmp_path / "results")

    findings = await RPCStage().run(asset)

    rule_ids = {finding.rule_id for finding in findings}
    assert "rpc-dynamic-method" in rule_ids
    assert "rpc-dynamic-fetch-url" in rule_ids
    assert any(finding.severity is Severity.HIGH for finding in findings)
    coverage = json.loads(
        (tmp_path / "results/workers/rpc/coverage.json").read_text(encoding="utf-8")
    )
    assert coverage["rpc_candidate_files"] == 1
    assert coverage["scope_files_scanned"] == 1


@pytest.mark.asyncio
async def test_rpc_allowlist_reduces_dynamic_method_severity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    asset = _asset(tmp_path)
    (asset.path / "provider.ts").write_text(
        "const allowedMethods = new Set(['eth_call']);\n"
        "provider.request({ method: request.method, params: [] });\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("ens_audit.pipeline.scan_utils.RESULTS_DIR", tmp_path / "results")

    findings = await RPCStage().run(asset)

    dynamic = next(f for f in findings if f.rule_id == "rpc-dynamic-method")
    assert dynamic.severity is Severity.MEDIUM
    assert dynamic.confidence == 0.58


@pytest.mark.asyncio
async def test_diff_stage_scans_only_added_lines_and_redacts_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    asset = _asset(tmp_path, "smart-account")
    patch = (
        "diff --git a/packages/smart-account/src/a.ts b/packages/smart-account/src/a.ts\n"
        "+++ b/packages/smart-account/src/a.ts\n"
        "@@ -4,0 +5,2 @@\n"
        "+const token = process.env.PRIVATE_KEY;\n"
        "+provider.request({ method: request.method });\n"
    )
    monkeypatch.setattr(stage_diff, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(stage_diff, "_repo_root", lambda _path: tmp_path)
    monkeypatch.setattr(stage_diff, "_first_parent", lambda _repo, _commit: "a" * 40)
    monkeypatch.setattr(stage_diff, "_diff", lambda _repo, _parent, _commit, _scope: patch)

    findings = await DiffStage().run(asset)

    assert {finding.rule_id for finding in findings} >= {
        "diff-secret-key",
        "diff-rpc-network",
    }
    serialized = json.dumps([finding.to_dict() for finding in findings])
    assert "PRIVATE_KEY" not in serialized
    coverage = json.loads(
        (tmp_path / "results/smart-account/diff/coverage.json").read_text(encoding="utf-8")
    )
    assert coverage["added_lines"] == 2
    assert coverage["status"] == "completed"
