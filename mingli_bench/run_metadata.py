"""Small helpers for reproducible run metadata."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


def build_run_metadata(*, root: Optional[Path] = None) -> Dict[str, Any]:
    """Return lightweight metadata useful for reproducing eval runs."""

    repo_root = root or Path(__file__).resolve().parents[1]
    return {
        "git_commit": _git_output(["rev-parse", "HEAD"], repo_root),
        "git_dirty": _git_dirty(repo_root),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def _git_output(args: list[str], root: Path) -> Optional[str]:
    return _git_output_raw(args, root) or None


def _git_output_raw(args: list[str], root: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip()


def _git_dirty(root: Path) -> Optional[bool]:
    value = _git_output_raw(["status", "--porcelain"], root)
    if value is None:
        return None
    return bool(value)


__all__ = ["build_run_metadata"]
