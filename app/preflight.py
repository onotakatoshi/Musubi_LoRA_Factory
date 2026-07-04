from __future__ import annotations

from pathlib import Path

import toml

from model_adapters import get_adapter
from model_registry import get_profile
from path_resolver import resolve_path


def _status_path(label: str, value: str, must_exist: bool = True) -> str:
    if not value:
        return f"❌ {label}: not set"
    p = resolve_path(value)
    if must_exist and not p.exists():
        return f"❌ {label}: not found: {p}  (settings: {value})"
    return f"✅ {label}: {p}  (settings: {value})"


def run_preflight(settings_path: Path, dataset_toml: str, target_model: str, task: str) -> str:
    profile = get_profile(target_model)
    lines = [
        "# Preflight Check",
        "",
        "Ver 1.0 は Z-Image / Z-Image-Turbo 用LoRA作成に限定しています。",
        "パス検証はモデルアダプタ経由です。Musubi Tuner対応モデルを後から追加しやすい構造にしています。",
        "Relative paths are resolved from the repository root.",
        "",
    ]

    if not profile.enabled_in_v1:
        return f"❌ Ver 1.0 では {profile.display_name} は非対応です。Z-Image / Z-Image-Turbo の検証後に追加します。"
    if task != profile.task:
        return f"❌ Ver 1.0 の {profile.display_name} profile は task={profile.task} 固定です。"

    if not settings_path.exists():
        return f"❌ settings.toml がありません: {settings_path}\nアプリの設定タブ、または configs/settings.example.toml から作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    paths = data.get("paths", {})
    model_paths = data.get("model_paths", {})

    lines.append("## profile")
    lines.append(f"✅ profile: {profile.display_name}")
    lines.append(f"✅ task: {profile.task}")
    lines.append("")

    lines.append("## musubi-tuner")
    lines.append(_status_path("repo_path", musubi.get("repo_path", "")))
    lines.append(_status_path("python_path", musubi.get("python_path", "")))
    lines.append("")

    lines.append("## app paths")
    lines.append(_status_path("datasets_dir", paths.get("datasets_dir", ""), must_exist=False))
    lines.append(_status_path("outputs_dir", paths.get("outputs_dir", ""), must_exist=False))
    lines.append(_status_path("comfyui_loras_dir", paths.get("comfyui_loras_dir", ""), must_exist=False))
    lines.append("")

    lines.append("## dataset")
    if dataset_toml:
        lines.append(_status_path("dataset.toml", dataset_toml))
    else:
        lines.append("❌ dataset.toml: not set")
    lines.append("")

    try:
        adapter = get_adapter(profile.id)
    except NotImplementedError as exc:
        lines.append(f"❌ {exc}")
        text = "\n".join(lines)
        return text + "\n\nResult: ❌ このモデルのPreflightはまだ実装していません。"

    lines.append(f"## {profile.display_name} model paths")
    missing = set(adapter.validate_model_paths(model_paths))
    for key in adapter.required_setting_keys():
        label = f"model_paths.{key}"
        lines.append(_status_path(key, model_paths.get(key, "")) if label not in missing else f"❌ {label}: not set")
    for key in adapter.optional_setting_keys():
        value = model_paths.get(key, "")
        if value:
            lines.append(_status_path(key, value))
        else:
            lines.append(f"ℹ️ model_paths.{key}: optional / not set")
    lines.append("")

    if profile.id == "z-image":
        lines.append("## Z-Image note")
        lines.append("- Turbo系そのものを直接学習するより、BaseまたはDe-Turbo系DiTを学習対象にする想定です。")
        lines.append("- 生成時にZ-Image-TurboワークフローへLoRAを適用する運用を優先します。")
        lines.append("")

    text = "\n".join(lines)
    if "❌" in text:
        text += "\n\nResult: ❌ 実行前に不足項目を直してください。"
    else:
        text += "\n\nResult: ✅ 実行準備OKです。Preview Commandsで内容を確認してください。"
    return text
