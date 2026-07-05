from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def load(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise SystemExit("Python 3.11+ is required, or install tomli/toml.")
    with path.open("rb") as f:
        return tomllib.load(f)


def _value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int | float):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_value(x) for x in v) + "]"
    return json.dumps("" if v is None else str(v), ensure_ascii=False)


def dumps(data: dict[str, Any]) -> str:
    lines: list[str] = []
    plain = {k: v for k, v in data.items() if not isinstance(v, dict)}
    sections = {k: v for k, v in data.items() if isinstance(v, dict)}

    for key, val in plain.items():
        lines.append(f"{key} = {_value(val)}")
    if plain and sections:
        lines.append("")

    for section, values in sections.items():
        lines.append(f"[{section}]")
        for key, val in values.items():
            if isinstance(val, dict):
                continue
            lines.append(f"{key} = {_value(val)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
