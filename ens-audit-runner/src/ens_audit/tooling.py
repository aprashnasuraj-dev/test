"""Safe native/WSL tool discovery and argv-only process execution."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

_WINDOWS_ABSOLUTE = re.compile(r"^(?P<drive>[A-Za-z]):[\\/](?P<tail>.*)$")
_WINDOWS_FILE_URI = re.compile(r"^file:///(?P<drive>[A-Za-z]):/(?P<tail>.*)$")


@dataclass(frozen=True, slots=True)
class ResolvedTool:
    """Describe where one external executable will run."""

    name: str
    mode: str
    executable: str


@dataclass(slots=True)
class ToolRunner:
    """Resolve tools natively first, then through WSL without shell command strings.

    Security invariant: every process is invoked as an argv sequence with ``shell=False``.
    WSL fallback uses ``wsl.exe -e`` and transforms only absolute Windows filesystem paths.
    """

    session_environment: dict[str, str] = field(default_factory=dict)
    _cache: dict[str, ResolvedTool | None] = field(default_factory=dict, init=False)
    _wsl_path_cache: dict[str, str | None] = field(default_factory=dict, init=False)

    def set_session_environment(self, values: Mapping[str, str]) -> None:
        """Replace in-memory tool credentials without persisting or logging their values."""

        self.session_environment = {key: value for key, value in values.items() if value}

    def clear_cache(self) -> None:
        """Discard executable discovery results after tools are installed or PATH changes."""

        self._cache.clear()
        self._wsl_path_cache.clear()

    @staticmethod
    def native_path(tool: str) -> str | None:
        """Return the native PATH resolution for a tool without executing it."""

        return shutil.which(tool)

    def wsl_path(self, tool: str) -> str | None:
        """Return the executable path inside the default WSL distribution, if installed."""

        if tool in self._wsl_path_cache:
            return self._wsl_path_cache[tool]
        wsl = shutil.which("wsl.exe") or shutil.which("wsl")
        if not wsl:
            self._wsl_path_cache[tool] = None
            return None
        probe = subprocess.run(
            [wsl, "-e", "which", tool],
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        path = probe.stdout.strip() if probe.returncode == 0 else ""
        result = path if path.startswith("/") else None
        self._wsl_path_cache[tool] = result
        return result

    def resolve(self, tool: str) -> ResolvedTool | None:
        """Resolve a command on native PATH or inside the default WSL distribution."""

        if tool in self._cache:
            return self._cache[tool]

        native = self.native_path(tool)
        if native:
            resolved = ResolvedTool(tool, "native", native)
            self._cache[tool] = resolved
            return resolved

        wsl = shutil.which("wsl.exe") or shutil.which("wsl")
        if wsl and self.wsl_path(tool):
            resolved = ResolvedTool(tool, "wsl", wsl)
            self._cache[tool] = resolved
            return resolved

        self._cache[tool] = None
        return None

    def available(self, tool: str) -> bool:
        """Return whether a native or WSL executable is available."""

        return self.resolve(tool) is not None

    def run(
        self,
        tool: str,
        args: Sequence[str],
        *,
        cwd: Path,
        timeout_s: int,
        extra_environment: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a resolved executable and return its completed process object."""

        resolved = self.resolve(tool)
        if resolved is None:
            raise FileNotFoundError(f"required analyzer is not installed: {tool}")

        merged_env = os.environ.copy()
        merged_env.update(self.session_environment)
        if extra_environment:
            merged_env.update({key: value for key, value in extra_environment.items() if value})

        if resolved.mode == "native":
            argv = [resolved.executable, *args]
            process_cwd: str | Path | None = cwd
        else:
            wsl_cwd = windows_path_to_wsl(str(cwd.resolve()))
            converted = [convert_argument_for_wsl(value) for value in args]
            argv = [resolved.executable, "--cd", wsl_cwd, "-e", tool, *converted]
            process_cwd = None
            merged_env["WSLENV"] = _merge_wslenv(
                merged_env.get("WSLENV", ""), tuple(self.session_environment) + tuple(extra_environment or {})
            )

        return subprocess.run(
            argv,
            cwd=process_cwd,
            env=merged_env,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )


def windows_path_to_wsl(value: str) -> str:
    """Convert an absolute drive-letter Windows path to its WSL mount path."""

    match = _WINDOWS_ABSOLUTE.match(value)
    if not match:
        if value.startswith("/"):
            return value
        raise ValueError(f"WSL fallback requires an absolute drive-letter path: {value}")
    tail = match.group("tail").replace("\\", "/")
    return f"/mnt/{match.group('drive').lower()}/{tail}"


def convert_argument_for_wsl(value: str) -> str:
    """Convert absolute Windows paths embedded in common argv token shapes."""

    uri_match = _WINDOWS_FILE_URI.match(value)
    if uri_match:
        tail = uri_match.group("tail").replace("\\", "/")
        return f"file:///mnt/{uri_match.group('drive').lower()}/{tail}"

    if _WINDOWS_ABSOLUTE.match(value):
        return windows_path_to_wsl(value)

    if "=" in value:
        prefix, candidate = value.split("=", 1)
        if _WINDOWS_ABSOLUTE.match(candidate):
            return f"{prefix}={windows_path_to_wsl(candidate)}"
    return value


def _merge_wslenv(existing: str, names: Sequence[str]) -> str:
    """Forward selected session environment variables through WSL without argv exposure."""

    entries = [entry for entry in existing.split(":") if entry]
    existing_names = {entry.split("/", 1)[0] for entry in entries}
    for name in names:
        if name and name not in existing_names:
            entries.append(f"{name}/u")
            existing_names.add(name)
    return ":".join(entries)


DEFAULT_TOOL_RUNNER = ToolRunner()
