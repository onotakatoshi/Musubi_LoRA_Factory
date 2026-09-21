"""Environment shared by every musubi-tuner subprocess the app starts.

Triton compiles kernels into ~/.triton/cache. If that directory ends up owned by
another user (it happens when something was once run under sudo), every run dies with
a PermissionError deep inside torch. Falling back to a writable cache dir keeps the
compiled kernels cached without needing root to repair the original directory.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

FALLBACK_TRITON_CACHE = Path.home() / ".cache" / "triton_musubi"


def _is_writable_dir(path: Path) -> bool:
    try:
        if path.exists():
            return path.is_dir() and os.access(path, os.W_OK | os.X_OK)
        parent = path.parent
        return parent.is_dir() and os.access(parent, os.W_OK | os.X_OK)
    except OSError:
        return False


def writable_triton_cache_dir() -> str | None:
    """Return a cache dir to force, or None when the default is already fine."""
    if os.environ.get("TRITON_CACHE_DIR"):
        return None
    default_cache = Path.home() / ".triton" / "cache"
    if _is_writable_dir(default_cache):
        return None
    for candidate in (FALLBACK_TRITON_CACHE, Path(tempfile.gettempdir()) / "triton_musubi"):
        if _is_writable_dir(candidate):
            candidate.mkdir(parents=True, exist_ok=True)
            return str(candidate)
    return None


def subprocess_env_overrides() -> dict[str, str]:
    overrides = {"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}
    triton_cache = writable_triton_cache_dir()
    if triton_cache:
        overrides["TRITON_CACHE_DIR"] = triton_cache
    return overrides


def subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    env.update(subprocess_env_overrides())
    return env
