from __future__ import annotations

from pathlib import Path

import toml

from commands import ModelPaths, build_command_preview

SUPPORTED_TARGET_MODEL = "z-image"
SUPPORTED_TASK = "z-image"


def _paths_for_zimage(model_paths: dict) -> ModelPaths:
    return ModelPaths(
        vae=model_paths.get("zimage_vae", ""),
        dit=model_paths.get("zimage_dit", ""),
        text_encoder=model_paths.get("zimage_text_encoder", ""),
        base_weights=model_paths.get("zimage_base_weights", ""),
    )


def preview_from_settings(
    settings_path: Path,
    dataset_toml: str,
    target_model: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    output_name: str,
    task: str,
) -> str:
    if target_model != SUPPORTED_TARGET_MODEL:
        return "NG: Ver 1.0 は Z-Image 専用です。Target model は z-image 固定です。"
    if task != SUPPORTED_TASK:
        return "NG: Ver 1.0 は Z-Image 専用です。Task/profile は z-image 固定です。"
    if not settings_path.exists():
        return f"NG: settings.toml がありません: {settings_path}"
    if not dataset_toml:
        return "NG: dataset.toml を先に作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    model_paths = data.get("model_paths", {})
    dataset_path = Path(dataset_toml)
    output_dir = dataset_path.parent
    paths = _paths_for_zimage(model_paths)

    missing = []
    if not paths.vae:
        missing.append("model_paths.zimage_vae")
    if not paths.dit:
        missing.append("model_paths.zimage_dit")
    if not paths.text_encoder:
        missing.append("model_paths.zimage_text_encoder")
    if missing:
        return "NG: settings.toml の以下を設定してください。\n" + "\n".join(f"- {m}" for m in missing)

    command = build_command_preview(
        target_model=SUPPORTED_TARGET_MODEL,
        musubi_python=Path(musubi.get("python_path", "python")),
        musubi_repo=Path(musubi.get("repo_path", ".")),
        dataset_toml=dataset_path,
        output_dir=output_dir,
        output_name=output_name,
        paths=paths,
        rank=rank,
        alpha=alpha,
        epochs=epochs,
        lr=lr,
        task=SUPPORTED_TASK,
    )

    return (
        "# Command Preview\n"
        "# Ver 1.0 は Z-Image / Z-Image-Turbo 用LoRA作成に限定しています。\n"
        "# 内容を確認し、問題なければPGX上で順番に実行してください。\n\n"
        + command
    )
