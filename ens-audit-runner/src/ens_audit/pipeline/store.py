"""SQLite persistence for audit runs, checkpoints, and normalized findings."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID, uuid4

from ens_audit.models import Finding, FindingStatus, Location, Severity

_DEFAULT_ANALYSIS_STAGES = ("sast", "symbolic", "fuzz", "deps", "secrets")
_DEFAULT_ANALYSIS_STAGES_JSON = json.dumps(_DEFAULT_ANALYSIS_STAGES, separators=(",", ":"))


class AnalysisStore:
    """Persist audit state in SQLite.

    Security invariant: all values are passed through parameterized statements; findings are
    never interpolated into SQL text.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Open a hardened SQLite connection for one operation."""

        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys=ON")
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        """Create required tables and migrate legacy run metadata in place."""

        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    commit_sha TEXT NOT NULL,
                    analysis_stages TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS stage_checkpoints (
                    run_id TEXT NOT NULL,
                    asset TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    succeeded INTEGER NOT NULL,
                    PRIMARY KEY (run_id, asset, stage),
                    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    asset TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
                );
                """
            )
            columns = {
                str(row["name"])
                for row in connection.execute("PRAGMA table_info(runs)").fetchall()
            }
            if "analysis_stages" not in columns:
                default_json = _DEFAULT_ANALYSIS_STAGES_JSON.replace("'", "''")
                connection.execute(
                    "ALTER TABLE runs ADD COLUMN analysis_stages TEXT NOT NULL "
                    f"DEFAULT '{default_json}'"
                )

    def begin_run(
        self,
        commit_sha: str,
        analysis_stages: tuple[str, ...] = _DEFAULT_ANALYSIS_STAGES,
    ) -> UUID:
        """Create a new immutable audit run with its intended analysis-stage selection."""

        run_id = uuid4()
        stage_json = json.dumps(analysis_stages, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO runs(id, commit_sha, analysis_stages) VALUES(?, ?, ?)",
                (str(run_id), commit_sha, stage_json),
            )
        return run_id

    def run_commit(self, run_id: UUID) -> str:
        """Return the immutable source commit associated with a run."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT commit_sha FROM runs WHERE id=?",
                (str(run_id),),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown audit run: {run_id}")
        return str(row["commit_sha"])

    def run_analysis_stages(self, run_id: UUID) -> tuple[str, ...]:
        """Return the canonical analysis-stage selection stored for a run."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT analysis_stages FROM runs WHERE id=?",
                (str(run_id),),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown audit run: {run_id}")
        raw = json.loads(str(row["analysis_stages"]))
        if not isinstance(raw, list) or not raw or not all(isinstance(item, str) for item in raw):
            raise ValueError(f"invalid stage selection stored for audit run: {run_id}")
        return tuple(raw)

    def save_stage(
        self,
        run_id: UUID,
        asset: str,
        stage: str,
        findings: list[Finding],
        *,
        succeeded: bool,
    ) -> None:
        """Atomically persist a stage's findings and checkpoint.

        Security invariant: either every finding and the checkpoint commit together or none
        of them do.
        """

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for finding in findings:
                connection.execute(
                    "INSERT OR REPLACE INTO findings(id, run_id, asset, stage, payload) "
                    "VALUES(?, ?, ?, ?, ?)",
                    (
                        str(finding.id),
                        str(run_id),
                        asset,
                        stage,
                        json.dumps(finding.to_dict(), sort_keys=True),
                    ),
                )
            connection.execute(
                "INSERT OR REPLACE INTO stage_checkpoints(run_id, asset, stage, succeeded) "
                "VALUES(?, ?, ?, ?)",
                (str(run_id), asset, stage, int(succeeded)),
            )
            connection.commit()

    def completed_stages(self, run_id: UUID, asset: str) -> set[str]:
        """Return successful stage names already checkpointed for one asset."""

        with self._connect() as connection:
            rows = connection.execute(
                "SELECT stage FROM stage_checkpoints "
                "WHERE run_id=? AND asset=? AND succeeded=1",
                (str(run_id), asset),
            ).fetchall()
        return {str(row["stage"]) for row in rows}

    def load_findings(self, run_id: UUID) -> list[Finding]:
        """Load normalized findings for one run in insertion order."""

        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM findings WHERE run_id=? ORDER BY rowid",
                (str(run_id),),
            ).fetchall()
        return [self._decode_finding(str(row["payload"])) for row in rows]

    @staticmethod
    def _decode_finding(payload: str) -> Finding:
        """Reconstruct a finding from its inert JSON representation."""

        data = json.loads(payload)
        location_data = data.pop("location")
        data["id"] = UUID(data["id"])
        data["severity"] = Severity(data["severity"])
        data["status"] = FindingStatus(data["status"])
        data["references"] = tuple(data.get("references", ()))
        data["location"] = Location(**location_data)
        return Finding(**data)
