from __future__ import annotations

from pathlib import Path

import toml

from commands import ModelPaths, build_command_preview
from model_registry import get_profile


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
    profile = get_profile(target_model)
    if not profile.enabled_in_v1:
        return f"NG: Ver 1.0 では {profile.display_name} は非対応です。Z-Image / Z-Image-Turbo の検証後に追加します。"
    if task != profile.task:
        return f"NG: Ver 1.0 の {profile.display_name} profile は task={profile.task} 固定です。"
    if not settings_path.exists():
        return f"NG: settings.toml がありません: {settings_path}"
    if not dataset_toml:
        return "NG: dataset.toml を先に作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    model_paths = data.get("model_paths", {})
    dataset_path = Path(dataset_toml)
    output_dir = dataset_path.parent

    if profile.id != "z-image":
        return f"NG: {profile.display_name} のコマンド生成はまだ実装していません。"

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
        target_model=profile.id,
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
        task=profile.task,
    )

    return (
        "# Command Preview\n"
        "# Ver 1.0 は Z-Image / Z-Image-Turbo 用LoRA作成に限定しています。\n"
        "# ただし内部構造はモデルプロファイル追加を前提にしています。\n"
        "# 内容を確認し、問題なければPGX上で順番に実行してください。\n\n"
        + command
    )
