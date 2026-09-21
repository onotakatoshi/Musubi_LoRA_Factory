from __future__ import annotations

from pathlib import Path

from i18n import normalize_language
from model_adapters import adapter_ids, get_adapter
from model_registry import PROFILES, ModelProfile, get_profile, normalize_profile_id, profile_ids
from model_ui import WIRED_PROFILE_IDS, available_model_labels, v1_default_profile
from settings_io import load_settings, nested_get

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"


def selected_profile(settings: dict | None) -> tuple[ModelProfile, str | None]:
    """Resolve the profile the app will actually open with.

    Returns the profile and, when the configured value could not be used, a note
    explaining the fallback. Reporting the registry default here regardless of
    ui.target_model made the check claim readiness for the wrong model.
    """
    fallback = v1_default_profile()
    if not settings:
        return fallback, None

    configured = nested_get(settings, "ui", "target_model").strip()
    if not configured:
        return fallback, None

    resolved = normalize_profile_id(configured)
    if resolved not in PROFILES:
        return fallback, f"⚠️ ui.target_model '{configured}' is not a known profile; using {fallback.display_name}."
    if resolved not in WIRED_PROFILE_IDS:
        return fallback, f"⚠️ ui.target_model '{configured}' is not in the Target model list; using {fallback.display_name}."
    return get_profile(resolved), None


def startup_check() -> str:
    lines = ["# Startup Check", ""]
    lines.append(f"Repository root: {ROOT}")
    lines.append(f"Settings file: {SETTINGS_PATH}")
    lines.append("")

    settings = load_settings(SETTINGS_PATH) if SETTINGS_PATH.exists() else None
    profile, fallback_note = selected_profile(settings)

    lines.append("## model profile")
    lines.append(f"✅ selected profile: {profile.id} / {profile.display_name}")
    if fallback_note:
        lines.append(fallback_note)
    lines.append(f"✅ visible models: {', '.join(available_model_labels())}")
    lines.append(f"✅ enabled profile ids: {', '.join(profile_ids())}")
    lines.append(f"✅ adapter ids: {', '.join(adapter_ids())}")
    lines.append("")

    adapter = get_adapter(profile.id)
    lines.append("## adapter")
    lines.append(f"✅ required settings: {', '.join(adapter.required_setting_keys())}")
    optional = adapter.optional_setting_keys()
    lines.append(f"ℹ️ optional settings: {', '.join(optional) if optional else 'none'}")
    lines.append("")

    if settings is None:
        lines.append("⚠️ configs/settings.toml does not exist yet. Run scripts/setup.sh or copy configs/settings.example.toml.")
        return "\n".join(lines)

    lang = normalize_language(nested_get(settings, "ui", "language", "日本語"))
    lines.append("## settings")
    lines.append(f"✅ language: {lang}")
    lines.append(f"✅ musubi repo path field: {nested_get(settings, 'musubi', 'repo_path') or 'not set'}")
    lines.append(f"✅ datasets dir field: {nested_get(settings, 'paths', 'datasets_dir') or 'not set'}")
    lines.append(f"✅ outputs dir field: {nested_get(settings, 'paths', 'outputs_dir') or 'not set'}")
    lines.append("")

    # Required model paths for the selected profile, so the check reflects the model the
    # app will open with rather than a generic structural pass.
    model_paths = settings.get("model_paths", {}) if isinstance(settings.get("model_paths"), dict) else {}
    missing = adapter.validate_model_paths(model_paths)
    lines.append("## model paths")
    if missing:
        lines.append(f"⚠️ not set for {profile.display_name}:")
        lines.extend(f"   - {key}" for key in missing)
    else:
        lines.append(f"✅ required model paths are set for {profile.display_name}")
    lines.append("")

    lines.append("## result")
    lines.append(f"✅ Startup structure OK for {profile.display_name}")
    if missing:
        lines.append("ℹ️ 学習を実行する前に、設定タブで上記のパスを埋めてください。")
    return "\n".join(lines)


if __name__ == "__main__":
    print(startup_check())
