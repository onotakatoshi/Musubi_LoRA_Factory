from __future__ import annotations

from pathlib import Path

import toml

from commands import ModelPaths, build_command_preview


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
    if not settings_path.exists():
        return f"NG: settings.toml がありません: {settings_path}"
    if not dataset_toml:
        return "NG: dataset.toml を先に作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    model_paths = data.get("model_paths", {})
    dataset_path = Path(dataset_toml)
    output_dir = dataset_path.parent

    paths = ModelPaths(
        vae=model_paths.get("wan_vae", ""),
        t5=model_paths.get("wan_t5", ""),
        dit=model_paths.get("wan_dit", ""),
        dit_high_noise=model_paths.get("wan_dit_high_noise", ""),
    )

    missing = []
    if target_model == "wan2.2":
        if not paths.vae:
            missing.append("model_paths.wan_vae")
        if not paths.t5:
            missing.append("model_paths.wan_t5")
        if not paths.dit:
            missing.append("model_paths.wan_dit")
        if task in {"t2v-A14B", "i2v-A14B"} and not paths.dit_high_noise:
            missing.append("model_paths.wan_dit_high_noise")
    if missing:
        return "NG: settings.toml の以下を設定してください。\n" + "\n".join(f"- {m}" for m in missing)

    command = build_command_preview(
        target_model=target_model,
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
        task=task,
    )

    return (
        "# Command Preview\n"
        "# まず内容を確認してください。問題なければPGX上で実行コマンド接続に進みます。\n\n"
        + command
    )
