#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
SCRIPT_DIR = ROOT / "scripts"
for item in (APP_DIR, SCRIPT_DIR):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from model_path_autofill_recursive import detect_paths  # noqa: E402
from toml_compat import dumps as toml_dumps  # noqa: E402
from toml_compat import load as toml_load  # noqa: E402

DEFAULT_SETTINGS_PATH = ROOT / "configs" / "settings.toml"
DEFAULT_EXAMPLE_PATH = ROOT / "configs" / "settings.example.toml"
DEFAULT_MODELS_DIR = ROOT.parent / "models"


def load_settings(settings_path: Path) -> dict:
    if settings_path.exists():
        return toml_load(settings_path)
    if DEFAULT_EXAMPLE_PATH.exists():
        return toml_load(DEFAULT_EXAMPLE_PATH)
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync downloaded model paths into configs/settings.toml")
    parser.add_argument("--models-dir", default=str(DEFAULT_MODELS_DIR), help="model root, default: ../models")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS_PATH), help="settings.toml path")
    parser.add_argument("--keep-existing", action="store_true", help="do not overwrite non-empty values")
    parser.add_argument("--dry-run", action="store_true", help="show changes without writing")
    args = parser.parse_args()

    models_dir = Path(args.models_dir).expanduser().resolve()
    settings_path = Path(args.settings).expanduser().resolve()
    detected = detect_paths(models_dir)
    data = load_settings(settings_path)
    model_paths = data.setdefault("model_paths", {})

    print(f"Models dir: {models_dir}")
    print(f"Settings:   {settings_path}")
    print(f"Detected:   {len(detected)}")

    changed = 0
    for key, value in sorted(detected.items()):
        old = str(model_paths.get(key, "") or "")
        if args.keep_existing and old:
            print(f"KEEP {key}: {old}")
            continue
        model_paths[key] = value
        if old == value:
            print(f"OK   {key}: {value}")
        else:
            print(f"SET  {key}: {value}")
            changed += 1

    print(f"Changed: {changed}")
    if args.dry_run:
        print("Dry run: settings.toml was not changed.")
        return 0

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(toml_dumps(data), encoding="utf-8")
    print(f"Wrote: {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
