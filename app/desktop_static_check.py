from __future__ import annotations

import ast
from pathlib import Path

from i18n import SUPPORTED_LANGUAGES, TEXT, tr
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

    # Import modules that desktop_main depends on, without starting QApplication.
    import caption_diagnostics  # noqa: F401
    import caption_table_widget  # noqa: F401
    import dataset_diagnostics  # noqa: F401
    import desktop_main  # noqa: F401
    import image_caption_browser  # noqa: F401
    import training_estimator  # noqa: F401

    print("Desktop static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
