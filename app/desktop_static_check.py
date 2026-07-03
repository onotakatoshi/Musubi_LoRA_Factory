from __future__ import annotations

import ast
from pathlib import Path

from i18n import SUPPORTED_LANGUAGES, TEXT, tr
from model_adapters import adapter_ids, get_adapter
from model_registry import PROFILES, enabled_profiles, get_profile, profile_ids, profile_summary
from model_ui import available_model_ids, available_model_labels, help_for_profile, label_for_profile, profile_id_from_label, task_for_profile, v1_default_profile
from recommended_defaults import DEFAULTS, help_text, status_text

ROOT = Path(__file__).resolve().parents[1]
DESKTOP_MAIN = ROOT / "app" / "desktop_main.py"
TRAINING_ENGINE = ROOT / "app" / "training_engine.py"
COMMANDS = ROOT / "app" / "commands.py"
COMMAND_PATH_GUARD = ROOT / "app" / "command_path_guard.py"
ENV_CHECK = ROOT / "app" / "env_check.py"

REQUIRED_I18N_KEYS = [
    "app_title", "tab_settings", "tab_system", "tab_dataset", "tab_caption", "tab_preview", "tab_config", "tab_train", "tab_export",
    "check_dataset", "diagnose_captions", "estimate_training_load", "preview_commands", "run_train", "copy_to_comfyui",
]
REQUIRED_DEFAULT_KEYS = ["resolution", "rank", "alpha", "epochs", "lr"]
FORBIDDEN_DESKTOP_MODEL_LITERALS = ["wan2.2", "t2v-A14B", "i2v-A14B", "t2v-1.3B"]


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


def _check_model_ui() -> None:
    assert available_model_ids() == ["z-image"]
    assert "wan2.2" in available_model_ids(include_future=True)
    assert available_model_labels() == ["Z-Image / Z-Image-Turbo"]
    assert label_for_profile("z-image") == "Z-Image / Z-Image-Turbo"
    assert profile_id_from_label("Z-Image / Z-Image-Turbo") == "z-image"
    assert task_for_profile("z-image") == "z-image"
    assert v1_default_profile().id == "z-image"
    assert "Z-Image" in help_for_profile("z-image", "日本語")
    assert "Z-Image" in help_for_profile("z-image", "English")


def _check_model_adapters() -> None:
    assert adapter_ids() == ["z-image"], "Only z-image adapter should be implemented for Ver 1.0"
    adapter = get_adapter("z-image")
    assert adapter.required_setting_keys() == ["zimage_vae", "zimage_dit", "zimage_text_encoder"]
    assert "zimage_base_weights" in adapter.optional_setting_keys()
    assert adapter.validate_model_paths({}) == ["model_paths.zimage_vae", "model_paths.zimage_dit", "model_paths.zimage_text_encoder"]
    assert adapter.validate_model_paths({"zimage_vae": "a", "zimage_dit": "b", "zimage_text_encoder": "c"}) == []


def _check_desktop_uses_model_ui() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    assert "available_model_labels" in text, "desktop_main.py should use model_ui.available_model_labels"
    assert "profile_id_from_label" in text, "desktop_main.py should convert labels through model_ui"
    assert "task_for_profile" in text, "desktop_main.py should sync task through model_ui"
    for literal in FORBIDDEN_DESKTOP_MODEL_LITERALS:
        assert literal not in text, f"desktop_main.py must not hard-code future model/task literal: {literal}"


def _check_desktop_uses_training_engine() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    assert "from training_engine import TrainingEngine" in text
    assert "self.training_engine = TrainingEngine()" in text
    assert "self.training_engine.prepare" in text
    assert "self.training_engine.run_one" in text
    assert "self.training_engine.run_all" in text
    assert "self.training_engine.stop" in text
    assert "_append_training_log" in text
    assert "_set_training_state" in text
    assert "全部実行" in text


def _check_training_engine_hardening() -> None:
    text = TRAINING_ENGINE.read_text(encoding="utf-8")
    assert "from command_path_guard import command_paths_ok" in text
    assert "infer_log_dir_from_sections" in text
    assert "waitForStarted(3000)" in text
    assert "errorOccurred.connect" in text
    assert "terminate()" in text
    assert "kill()" in text
    assert "COMMAND PATH GUARD FAILED" in text
    assert "Logs:" in text
    assert "QProcessEnvironment" in text
    assert "PYTHONUNBUFFERED" in text
    assert "PYTHONIOENCODING" in text
    assert "setProcessEnvironment" in text


def _check_commands_use_musubi_python() -> None:
    text = COMMANDS.read_text(encoding="utf-8")
    assert "accelerate_launch" in text
    assert "-m" in text and "accelerate.commands.launch" in text
    assert "accelerate launch" not in text
    assert "zimage_cache_latents.py" in text
    assert "zimage_cache_text_encoder_outputs.py" in text
    assert "zimage_train_network.py" in text


def _check_command_path_guard() -> None:
    text = COMMAND_PATH_GUARD.read_text(encoding="utf-8")
    assert "STAGES" in text
    assert "cwd" in text
    assert "python not found" in text
    assert "script not found" in text
    assert "--dataset_config" in text
    assert "--output_dir" in text
    assert "from training_engine" not in text, "command_path_guard must not import training_engine"


def _check_env_runtime_check() -> None:
    text = ENV_CHECK.read_text(encoding="utf-8")
    assert "from musubi_runtime_check import check_musubi_runtime" in text
    assert "## musubi runtime" in text


def _check_desktop_uses_output_detector() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    assert "from output_detector import find_latest_lora, output_summary" in text
    assert "find_latest_lora" in text
    assert "output_summary" in text
    assert "self.lora_path.setText" in text
    assert "書き出しタブのLoRAパスへ自動セット" in text


def _check_desktop_uses_export_validator() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")
    assert "from export_validator import validate_lora_for_export" in text
    assert "コピー前チェック" in text
    assert "def _validate_export" in text
    assert "validate_lora_for_export" in text
    assert "Result: OK" in text
    assert "copy_lora_to_comfyui" in text


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
    _check_model_ui()
    _check_model_adapters()
    _check_desktop_uses_model_ui()
    _check_desktop_uses_training_engine()
    _check_training_engine_hardening()
    _check_commands_use_musubi_python()
    _check_command_path_guard()
    _check_env_runtime_check()
    _check_desktop_uses_output_detector()
    _check_desktop_uses_export_validator()

    import caption_diagnostics  # noqa: F401
    import caption_table_widget  # noqa: F401
    import command_path_guard  # noqa: F401
    import dataset_diagnostics  # noqa: F401
    import desktop_main  # noqa: F401
    import export_validator  # noqa: F401
    import image_caption_browser  # noqa: F401
    import model_adapters  # noqa: F401
    import model_ui  # noqa: F401
    import musubi_runtime_check  # noqa: F401
    import output_detector  # noqa: F401
    import project_io  # noqa: F401
    import training_engine  # noqa: F401
    import training_estimator  # noqa: F401
    import training_presets  # noqa: F401
    import training_review  # noqa: F401

    print("Desktop static check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
