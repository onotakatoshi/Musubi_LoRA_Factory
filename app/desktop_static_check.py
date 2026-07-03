from __future__ import annotations

import ast
from pathlib import Path

from i18n import SUPPORTED_LANGUAGES, TEXT, tr
from model_registry import PROFILES, enabled_profiles, get_profile, profile_ids, profile_summary
from recommended_defaults import DEFAULTS, help_text, status_text

ROOT = Path(__file__).resolve().parents[1]
DESKTOP_MAIN = ROOT / "app" / "desktop_main.py"

REQUIRED_I18N_KEYS = [
    "app_title",
    "tab_settings",
    "tab_system",
    "tab_dataset",
    "tab_caption",
    "tab_preview",
    "tab_config",
    "tab_train",
    "tab_export",
    "check_dataset",
    "diagnose_captions",
    "estimate_training_load",
    "preview_commands",
    "run_train",
    "copy_to_comfyui",
]

REQUIRED_DEFAULT_KEYS = ["resolution", "rank", "alpha", "epochs", "lr"]


def _used_translation_keys() -> set[str]:
    tree = ast.parse(DESKTOP_MAIN.read_text(encoding="utf-8"))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            is_t_call = isinstance(func, ast.Attribute) and func.attr == "t"
            is_tr_call = isinstance(func, ast.Name) and func.id == "tr"
            if (is_t_call or is_tr_call) and node.args:
                arg = node.args[0] if is_t_call else (node.args[1] if len(node.args) > 1 else None)
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    keys.add(arg.value)
    return keys


def _check_model_registry() -> None:
    assert "z-image" in PROFILES, "z-image profile is required"
    assert get_profile("z-image").enabled_in_v1 is True, "z-image must be enabled in Ver 1.0"
    assert profile_ids() == ["z-image"], "Ver 1.0 should expose only z-image"
    assert "wan2.2" in profile_ids(include_future=True), "wan2.2 future profile should remain registered"
    assert get_profile("wan2.2").enabled_in_v1 is False, "wan2.2 must remain hidden until Z-Image validation is complete"
    for profile_id, profile in PROFILES.items():
        assert profile.id == profile_id, f"Profile key/id mismatch: {profile_id}"
        assert profile.display_name, f"Missing display name: {profile_id}"
        assert profile.task, f"Missing task: {profile_id}"
        assert profile.description_ja, f"Missing Japanese description: {profile_id}"
        assert profile.description_en, f"Missing English description: {profile_id}"
        assert profile_summary(profile_id, "日本語"), f"Missing Japanese summary: {profile_id}"
        assert profile_summary(profile_id, "English"), f"Missing English summary: {profile_id}"
    assert [p.id for p in enabled_profiles()] == ["z-image"], "Only z-image should be enabled for Ver 1.0"


def main() -> int:
    for lang in SUPPORTED_LANGUAGES:
        missing = [key for key in REQUIRED_I18N_KEYS if key not in TEXT[lang]]
        assert not missing, f"Missing required i18n keys for {lang}: {missing}"
        for key in REQUIRED_I18N_KEYS:
            assert tr(lang, key), f"Empty translation: {lang}:{key}"

    used = _used_translation_keys()
    for lang in SUPPORTED_LANGUAGES:
        missing_used = sorted(key for key in used if key not in TEXT[lang])
        assert not missing_used, f"desktop_main.py uses undefined i18n keys for {lang}: {missing_used}"

    for key in REQUIRED_DEFAULT_KEYS:
        assert key in DEFAULTS, f"Missing default key: {key}"
        assert help_text(key, "日本語"), f"Missing Japanese default help: {key}"
        assert help_text(key, "English"), f"Missing English default help: {key}"
        assert "推奨デフォルト" in status_text(key, DEFAULTS[key], "日本語"), key
        assert "Recommended default" in status_text(key, DEFAULTS[key], "English"), key

    _check_model_registry()

    import caption_diagnostics  # noqa: F401
    import caption_table_widget  # noqa: F401
    import dataset_diagnostics  # noqa: F401
    import desktop_main  # noqa: F401
    import image_caption_browser  # noqa: F401
    import project_io  # noqa: F401
    import training_estimator  # noqa: F401
    import training_presets  # noqa: F401
    import training_review  # noqa: F401

    print("Desktop static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
