from __future__ import annotations

STAGE_NAMES = {
    "latent_cache": "Latent Cache",
    "text_cache": "Text Encoder Cache",
    "train": "Train LoRA",
}

GUIDANCE = {
    "latent_cache": [
        "dataset.toml を確認してください。",
        "VAE のパスを確認してください。",
        "画像フォルダと出力フォルダを確認してください。",
    ],
    "text_cache": [
        "dataset.toml とcaptionを確認してください。",
        "Text Encoder のパスを確認してください。",
        "captionの空欄や文字化けを確認してください。",
    ],
    "train": [
        "DiT / VAE / Text Encoder のパスを確認してください。",
        "musubi python と accelerate を確認してください。",
        "rank、resolution、epoch設定を見直してください。",
    ],
}


def stage_display_name(stage: str) -> str:
    return STAGE_NAMES.get(stage, stage)


def guidance_for_stage(stage: str, exit_code: int | None = None, log_path: str | None = None) -> str:
    lines = [f"# {stage_display_name(stage)} failed", ""]
    if exit_code is not None:
        lines.append(f"Exit code: {exit_code}")
    if log_path:
        lines.append(f"Log file: {log_path}")
    lines.append("")
    lines.append("## 次に確認すること")
    for item in GUIDANCE.get(stage, ["ログを確認してください。"]):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("ログ解析、事前チェック、コマンド確認を再実行してください。")
    return "\n".join(lines)


def success_guidance_for_stage(stage: str, log_path: str | None = None) -> str:
    lines = [f"# {stage_display_name(stage)} done", ""]
    if log_path:
        lines.append(f"Log file: {log_path}")
        lines.append("")
    if stage == "latent_cache":
        lines.append("Next: Text Encoder Cache を実行してください。")
    elif stage == "text_cache":
        lines.append("Next: Train LoRA を実行してください。")
    elif stage == "train":
        lines.append("Next: 書き出しタブでコピー前チェックを実行してください。")
    else:
        lines.append("Next: 次のステップへ進んでください。")
    return "\n".join(lines)
