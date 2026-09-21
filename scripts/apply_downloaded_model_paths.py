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

# The candidate table lives in app/model_path_autofill.py so the GUI, this script and
# scripts/sync_model_paths.py can never drift apart again. A private copy here is what
# left every DiT pointing at a *.safetensors.index.json manifest musubi-tuner cannot read.
from model_file_format import resolve_model_file  # noqa: E402
from model_path_autofill import CANDIDATES as MODEL_PATH_CANDIDATES  # noqa: E402
from model_settings_catalog import all_model_path_keys  # noqa: E402
from toml_compat import dumps as toml_dumps  # noqa: E402
from toml_compat import load as toml_load  # noqa: E402

DEFAULT_SETTINGS = ROOT / "configs" / "settings.toml"
DEFAULT_EXAMPLE = ROOT / "configs" / "settings.example.toml"
DEFAULT_MODELS_DIR = Path.home() / "models"


def repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def setting_value_for(path: Path) -> str:
    try:
        return "../" + path.relative_to(ROOT.parent).as_posix()
    except ValueError:
        return path.as_posix()


def first_existing(models_dir: Path, candidates: list[str]) -> Path | None:
    for rel in candidates:
        if any(ch in rel for ch in "*?[]"):
            matches = sorted(p for p in models_dir.glob(rel) if p.exists())
        else:
            candidate = models_dir / rel
            matches = [candidate] if candidate.exists() else []
        for match in matches:
            resolved = resolve_model_file(match)
            if resolved is not None:
                return resolved
    return None


def load_settings(path: Path) -> dict:
    if path.exists():
        return toml_load(path)
    if DEFAULT_EXAMPLE.exists():
        return toml_load(DEFAULT_EXAMPLE)
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply downloaded model paths to configs/settings.toml")
    parser.add_argument("--models-dir", default=str(DEFAULT_MODELS_DIR), help="download root, default: ~/models")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS), help="settings.toml path")
    parser.add_argument("--dry-run", action="store_true", help="show changes without writing")
    parser.add_argument("--keep-existing", action="store_true", help="do not overwrite non-empty existing values")
    args = parser.parse_args()

    models_dir = Path(args.models_dir).expanduser().resolve()
    settings_path = Path(args.settings).expanduser().resolve()
    data = load_settings(settings_path)
    data.setdefault("model_paths", {})
    model_paths = data["model_paths"]

    print(f"Models dir:   {models_dir}")
    print(f"Settings file: {settings_path}")
    print("")

    updated = 0
    missing = 0
    kept = 0

    for key in all_model_path_keys():
        candidates = MODEL_PATH_CANDIDATES.get(key, [])
        old_value = str(model_paths.get(key, "") or "")
        if args.keep_existing and old_value:
            print(f"KEEP  {key}: {old_value}")
            kept += 1
            continue
        found = first_existing(models_dir, candidates)
        if found is None:
            model_paths.setdefault(key, old_value)
            print(f"MISS  {key}")
            missing += 1
            continue
        new_value = setting_value_for(found)
        model_paths[key] = new_value
        if new_value != old_value:
            print(f"SET   {key}: {new_value}")
            updated += 1
        else:
            print(f"OK    {key}: {new_value}")

    print("")
    print(f"Summary: updated={updated}, kept={kept}, missing={missing}")

    if args.dry_run:
        print("Dry run: settings.toml was not changed.")
        return 0

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(toml_dumps(data), encoding="utf-8")
    print(f"Wrote: {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
