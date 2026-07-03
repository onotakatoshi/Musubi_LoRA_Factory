from __future__ import annotations

from pathlib import Path

import toml

SUPPORTED_TARGET_MODEL = "z-image"
SUPPORTED_TASK = "z-image"


def _status_path(label: str, value: str, must_exist: bool = True) -> str:
    if not value:
        return f"❌ {label}: not set"
    p = Path(value)
    if must_exist and not p.exists():
        return f"❌ {label}: not found: {value}"
    return f"✅ {label}: {value}"


def run_preflight(settings_path: Path, dataset_toml: str, target_model: str, task: str) -> str:
    lines = ["# Preflight Check", "", "Ver 1.0 は Z-Image / Z-Image-Turbo 用LoRA作成に限定しています。", ""]

    if target_model != SUPPORTED_TARGET_MODEL:
        return "❌ Ver 1.0 は Z-Image 専用です。Target model は z-image 固定です。"
    if task != SUPPORTED_TASK:
        return "❌ Ver 1.0 は Z-Image 専用です。Task/profile は z-image 固定です。"

    if not settings_path.exists():
        return f"❌ settings.toml がありません: {settings_path}\nアプリの設定タブ、または configs/settings.example.toml から作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    paths = data.get("paths", {})
    model_paths = data.get("model_paths", {})

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

    lines.append("## Z-Image model paths")
    lines.append(_status_path("zimage_vae", model_paths.get("zimage_vae", "")))
    lines.append(_status_path("zimage_text_encoder", model_paths.get("zimage_text_encoder", "")))
    lines.append(_status_path("zimage_dit", model_paths.get("zimage_dit", "")))
    base_weights = model_paths.get("zimage_base_weights", "")
    if base_weights:
        lines.append(_status_path("zimage_base_weights", base_weights))
    else:
        lines.append("ℹ️ zimage_base_weights: optional / not set")
    lines.append("")

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
