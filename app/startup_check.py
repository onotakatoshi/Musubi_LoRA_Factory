from __future__ import annotations

from pathlib import Path

from i18n import normalize_language
from model_adapters import adapter_ids, get_adapter
from model_registry import get_profile, profile_ids
from model_ui import available_model_labels, v1_default_profile
from settings_io import load_settings, nested_get

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"


def startup_check() -> str:
    lines = ["# Startup Check", ""]
    lines.append(f"Repository root: {ROOT}")
    lines.append(f"Settings file: {SETTINGS_PATH}")
    lines.append("")

    default_profile = v1_default_profile()
    lines.append("## model profile")
    lines.append(f"✅ default profile: {default_profile.id} / {default_profile.display_name}")
    lines.append(f"✅ visible models: {', '.join(available_model_labels())}")
    lines.append(f"✅ enabled profile ids: {', '.join(profile_ids())}")
    lines.append(f"✅ adapter ids: {', '.join(adapter_ids())}")
    lines.append("")

    adapter = get_adapter(default_profile.id)
    lines.append("## adapter")
    lines.append(f"✅ required settings: {', '.join(adapter.required_setting_keys())}")
    optional = adapter.optional_setting_keys()
    lines.append(f"ℹ️ optional settings: {', '.join(optional) if optional else 'none'}")
    lines.append("")

    if not SETTINGS_PATH.exists():
        lines.append("⚠️ configs/settings.toml does not exist yet. Run scripts/setup.sh or copy configs/settings.example.toml.")
        return "\n".join(lines)

    settings = load_settings(SETTINGS_PATH)
    lang = normalize_language(nested_get(settings, "ui", "language", "日本語"))
    lines.append("## settings")
    lines.append(f"✅ language: {lang}")
    lines.append(f"✅ musubi repo path field: {nested_get(settings, 'musubi', 'repo_path') or 'not set'}")
    lines.append(f"✅ datasets dir field: {nested_get(settings, 'paths', 'datasets_dir') or 'not set'}")
    lines.append(f"✅ outputs dir field: {nested_get(settings, 'paths', 'outputs_dir') or 'not set'}")
    lines.append("")

    profile = get_profile(default_profile.id)
    lines.append("## result")
    lines.append(f"✅ Startup structure OK for {profile.display_name}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(startup_check())
