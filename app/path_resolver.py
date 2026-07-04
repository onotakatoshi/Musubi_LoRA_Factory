from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve_path(value: str | Path | None, base_dir: Path = ROOT) -> Path:
    """Resolve settings paths consistently.

    Rules:
    - empty values stay empty as Path("")
    - environment variables and ~ are expanded
    - absolute paths are kept absolute
    - relative paths are resolved from the repository root
    """
    if value is None:
        return Path("")
    text = str(value).strip()
    if not text:
        return Path("")
    expanded = os.path.expandvars(os.path.expanduser(text))
    path = Path(expanded)
    if path.is_absolute():
        return path
    return base_dir / path


def resolve_path_str(value: str | Path | None, base_dir: Path = ROOT) -> str:
    return str(resolve_path(value, base_dir))
