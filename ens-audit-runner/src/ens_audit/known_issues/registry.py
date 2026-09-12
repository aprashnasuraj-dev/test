"""Typed loader for Immunefi's public ENS known-issue registry."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class MatchPattern:
    """One optional structural matcher for a disclosed issue.

    Security invariant: matchers are inert data; regex text is compiled only by the filtering
    stage with bounded input strings.
    """

    file_glob: str | None = None
    content_regex: str | None = None
    git_history: bool = False
    rule_id: str | None = None
    cwe: str | None = None
    function: str | None = None


@dataclass(frozen=True, slots=True)
class KnownIssue:
    """Represent one public known issue from the competition scope.

    Security invariant: every suppression candidate has a stable issue id and explicit root
    cause; area-only similarity is insufficient for suppression.
    """

    id: str
    severity: str
    asset: tuple[str, ...]
    title: str
    root_cause: str
    match_patterns: tuple[MatchPattern, ...]
    suppress_if: tuple[str, ...] = ()
    notes: str = ""


def _registry_path() -> Path:
    """Return the packaged registry path.

    Security invariant: callers cannot redirect the default loader outside package data.
    """

    resource = resources.files("ens_audit.known_issues").joinpath("known_issues.yaml")
    return Path(str(resource))


def load_known_issues(path: Path | None = None) -> tuple[KnownIssue, ...]:
    """Load and validate known issues from safe YAML data.

    Security invariant: ``safe_load`` is used and malformed records fail closed rather than
    silently becoming broad suppression rules.
    """

    source = path or _registry_path()
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise TypeError("known issue registry must contain a YAML list")
    issues: list[KnownIssue] = []
    seen_ids: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise TypeError("known issue entries must be mappings")
        issue = _parse_issue(item)
        if issue.id in seen_ids:
            raise ValueError(f"duplicate known issue id: {issue.id}")
        seen_ids.add(issue.id)
        issues.append(issue)
    return tuple(issues)


def _parse_issue(item: dict[str, Any]) -> KnownIssue:
    """Convert one YAML mapping into a validated ``KnownIssue``."""

    required = ("id", "severity", "asset", "title", "root_cause", "match_patterns")
    missing = [key for key in required if key not in item]
    if missing:
        raise ValueError(f"known issue missing required fields: {', '.join(missing)}")
    assets = item["asset"]
    patterns = item["match_patterns"]
    suppress_if = item.get("suppress_if", [])
    if not isinstance(assets, list) or not all(isinstance(value, str) for value in assets):
        raise TypeError("known issue asset must be a list of strings")
    if not isinstance(patterns, list):
        raise TypeError("known issue match_patterns must be a list")
    if not isinstance(suppress_if, list) or not all(
        isinstance(value, str) for value in suppress_if
    ):
        raise TypeError("known issue suppress_if must be a list of strings")
    return KnownIssue(
        id=str(item["id"]),
        severity=str(item["severity"]),
        asset=tuple(assets),
        title=str(item["title"]),
        root_cause=str(item["root_cause"]),
        match_patterns=tuple(_parse_pattern(pattern) for pattern in patterns),
        suppress_if=tuple(suppress_if),
        notes=str(item.get("notes", "")),
    )


def _parse_pattern(item: Any) -> MatchPattern:
    """Validate one matcher mapping and reject unknown keys."""

    if not isinstance(item, dict):
        raise TypeError("known issue match pattern must be a mapping")
    allowed = {"file_glob", "content_regex", "git_history", "rule_id", "cwe", "function"}
    unknown = set(item) - allowed
    if unknown:
        raise ValueError(f"unknown match pattern fields: {', '.join(sorted(unknown))}")
    git_history = item.get("git_history", False)
    if not isinstance(git_history, bool):
        raise TypeError("git_history match pattern must be a boolean")
    return MatchPattern(
        file_glob=_optional_string(item.get("file_glob")),
        content_regex=_optional_string(item.get("content_regex")),
        git_history=git_history,
        rule_id=_optional_string(item.get("rule_id")),
        cwe=_optional_string(item.get("cwe")),
        function=_optional_string(item.get("function")),
    )


def _optional_string(value: Any) -> str | None:
    """Return a validated optional string field."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("match pattern values must be strings")
    return value
