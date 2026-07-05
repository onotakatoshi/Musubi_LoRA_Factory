#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import toml

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from model_path_autofill_recursive import detect_paths  # noqa: E402
from model_registry import enabled_profiles  # noqa: E402
from model_settings_catalog import settings_spec  # noqa: E402

SETTINGS_PATH = ROOT / "configs" / "settings.toml"
MODELS_DIR = ROOT.parent / "models"


def resolve_setting_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (ROOT / path).resolve()


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return toml.load(SETTINGS_PATH)
    return {}


def main() -> int:
    data = load_settings()
    settings_paths = data.get("model_paths", {})
    detected_paths = detect_paths(MODELS_DIR)

    print(f"Settings: {SETTINGS_PATH}")
    print(f"Models:   {MODELS_DIR}")
    print(f"Detected: {len(detected_paths)}")
    print("")

    ok_profiles = 0
    partial_profiles = 0
    missing_profiles = 0

    for profile in enabled_profiles(include_future=True):
        spec = settings_spec(profile.id)
        required = [f for f in spec.fields if f.required]
        if not required:
            continue

        rows: list[str] = []
        ok_count = 0
        detected_count = 0
        for field in required:
            value = str(settings_paths.get(field.key, "") or "")
            detected = str(detected_paths.get(field.key, "") or "")
            effective = value or detected
            exists = bool(effective) and resolve_setting_path(effective).exists()
            if exists:
                ok_count += 1
                state = "OK"
            elif detected:
                detected_count += 1
                state = "DETECTED_NOT_SAVED"
            elif value:
                state = "SET_BUT_NOT_FOUND"
            else:
                state = "MISSING"
            shown = effective or ""
            rows.append(f"  {state:18} {field.key:28} {shown}")

        if ok_count == len(required):
            profile_state = "READY"
            ok_profiles += 1
        elif ok_count or detected_count:
            profile_state = "PARTIAL"
            partial_profiles += 1
        else:
            profile_state = "NOT_DOWNLOADED"
            missing_profiles += 1

        print(f"[{profile_state}] {profile.display_name} ({profile.id})")
        for row in rows:
            print(row)
        print("")

    print("Summary:")
    print(f"  READY:          {ok_profiles}")
    print(f"  PARTIAL:        {partial_profiles}")
    print(f"  NOT_DOWNLOADED: {missing_profiles}")
    print("")
    print("Next:")
    print("  python3 scripts/sync_model_paths.py")
    print("  python3 scripts/audit_model_assets.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
