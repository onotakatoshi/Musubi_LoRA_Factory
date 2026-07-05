#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import toml

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"
EXAMPLE_PATH = ROOT / "configs" / "settings.example.toml"

from model_path_autofill_recursive import detect_paths  # noqa: E402


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return toml.load(SETTINGS_PATH)
    if EXAMPLE_PATH.exists():
        return toml.load(EXAMPLE_PATH)
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
    SETTINGS_PATH.write_text(toml.dumps(data), encoding="utf-8")
    print(f"Wrote: {SETTINGS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
