from __future__ import annotations

from pathlib import Path

import toml

import training_tab_patch
from model_registry import get_profile

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"


def _settings_default_profile():
    try:
        if SETTINGS_PATH.exists():
            data = toml.load(SETTINGS_PATH)
            profile_id = str(data.get("ui", {}).get("target_model", "z-image"))
            return get_profile(profile_id)
    except Exception:
        pass
    return get_profile("z-image")


def apply_training_target_model_patch() -> None:
    training_tab_patch.v1_default_profile = _settings_default_profile
