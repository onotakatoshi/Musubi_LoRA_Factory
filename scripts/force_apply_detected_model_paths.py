#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
SCRIPT_DIR = ROOT / "scripts"
for item in (APP_DIR, SCRIPT_DIR):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

SETTINGS_PATH = ROOT / "configs" / "settings.toml"
EXAMPLE_PATH = ROOT / "configs" / "settings.example.toml"

from model_path_autofill_recursive import detect_paths  # noqa: E402
from toml_compat import dumps as toml_dumps  # noqa: E402
from toml_compat import load as toml_load  # noqa: E402


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return toml_load(SETTINGS_PATH)
    if EXAMPLE_PATH.exists():
        return toml_load(EXAMPLE_PATH)
    return {}


def main() -> int:
    detected = detect_paths()
    data = load_settings()
    model_paths = data.setdefault("model_paths", {})

    print(f"Settings: {SETTINGS_PATH}")
    print(f"Detected: {len(detected)}")
    for key, value in sorted(detected.items()):
        old = str(model_paths.get(key, "") or "")
        model_paths[key] = value
        if old == value:
            print(f"OK  {key}: {value}")
        else:
            print(f"SET {key}: {value}")

    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(toml_dumps(data), encoding="utf-8")
    print(f"Wrote: {SETTINGS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
