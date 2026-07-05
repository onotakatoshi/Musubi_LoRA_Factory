from __future__ import annotations

from pathlib import Path

import toml

from model_adapters import CommandContext, get_adapter
from model_registry import get_profile
from path_resolver import resolve_path, resolve_path_str


def _resolved_model_paths(model_paths: dict) -> dict:
    resolved = dict(model_paths)
    for key, value in list(resolved.items()):
        if isinstance(value, str) and value.strip():
            resolved[key] = resolve_path_str(value)
    return resolved


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
        return f"NG: {profile.display_name} はまだ非対応です。"
    if task != profile.task:
        return f"NG: {profile.display_name} profile は task={profile.task} 固定です。"
    if not settings_path.exists():
        return f"NG: settings.toml がありません: {settings_path}"
    if not dataset_toml:
        return "NG: dataset.toml を先に作成してください。"

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    model_paths = _resolved_model_paths(data.get("model_paths", {}))
    dataset_path = resolve_path(dataset_toml)
    output_dir = dataset_path.parent

    try:
        adapter = get_adapter(profile.id)
    except NotImplementedError as exc:
        return f"NG: {exc}"

    missing = adapter.validate_model_paths(model_paths)
    if missing:
        return "NG: settings.toml の以下を設定してください。\n" + "\n".join(f"- {m}" for m in missing)

    command = adapter.build_commands(
        CommandContext(
            musubi_python=resolve_path(musubi.get("python_path", "../musubi-tuner/.venv/bin/python")),
            musubi_repo=resolve_path(musubi.get("repo_path", "../musubi-tuner")),
            dataset_toml=dataset_path,
            output_dir=output_dir,
            output_name=output_name,
            model_paths=model_paths,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
        )
    )
    if command.startswith("NG:"):
        return command

    return (
        "# Command Preview\n"
        f"# Target model: {profile.display_name}\n"
        f"# Task: {profile.task}\n"
        "# コマンド生成はモデルアダプタ経由です。内容を確認し、問題なければPGX上で順番に実行してください。\n\n"
        + command
    )
