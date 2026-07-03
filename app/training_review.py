from __future__ import annotations

from pathlib import Path

from caption_diagnostics import diagnose_captions
from dataset_diagnostics import diagnose_dataset
from pipeline import image_files


def training_review(
    dataset_dir: Path,
    lora_type: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    resolution: int,
    dataset_toml: str,
    target_model: str,
    lang: str = "日本語",
) -> str:
    ja = lang != "English"
    imgs = image_files(dataset_dir)
    problems: list[str] = []
    warnings: list[str] = []

    if not imgs:
        problems.append("画像がありません。" if ja else "No images found.")
    if not dataset_toml:
        problems.append("dataset.toml が未作成です。" if ja else "dataset.toml is not set.")
    elif not Path(dataset_toml).exists():
        problems.append(("dataset.toml が存在しません: " if ja else "dataset.toml not found: ") + dataset_toml)
    if target_model != "z-image":
        warnings.append("初期版の優先対象は z-image です。" if ja else "Initial version is optimized for z-image.")
    if alpha != rank:
        warnings.append("AlphaがRankと異なります。意図した設定か確認してください。" if ja else "Alpha differs from Rank. Confirm this is intentional.")
    if rank >= 64 and len(imgs) < 100:
        warnings.append("画像数に対してRankが高めです。過学習に注意してください。" if ja else "Rank may be high for the dataset size. Watch for overfitting.")
    if epochs >= 30:
        warnings.append("Epochsが高めです。初回は10前後を推奨します。" if ja else "Epochs is high. Around 10 is recommended for the first run.")
    if resolution > 768:
        warnings.append("Resolutionが高めです。初回は512を推奨します。" if ja else "Resolution is high. 512 is recommended first.")
    if lr > 0.0001:
        warnings.append("Learning rateが高めです。学習が壊れる可能性があります。" if ja else "Learning rate is high and may destabilize training.")

    score = 5
    score -= len(problems) * 2
    score -= len(warnings)
    score = max(1, min(5, score))
    stars = "★" * score + "☆" * (5 - score)

    if ja:
        lines = [
            "# 学習前レビュー",
            "",
            f"評価: {stars}",
            f"Target model: {target_model}",
            f"LoRA type: {lora_type}",
            f"画像数: {len(imgs)}",
            f"Rank / Alpha: {rank} / {alpha}",
            f"Epochs: {epochs}",
            f"Learning rate: {lr}",
            f"Resolution: {resolution}",
            f"dataset.toml: {dataset_toml or '未設定'}",
        ]
        if problems:
            lines += ["", "## ❌ 先に直す項目"] + [f"- {p}" for p in problems]
        if warnings:
            lines += ["", "## ⚠️ 確認したほうがよい項目"] + [f"- {w}" for w in warnings]
        if not problems and not warnings:
            lines += ["", "✅ この設定で学習開始できます。"]
        elif not problems:
            lines += ["", "⚠️ 学習は開始できますが、警告内容を確認してください。"]
        else:
            lines += ["", "❌ 先にエラー項目を修正してください。"]
    else:
        lines = [
            "# Training Review",
            "",
            f"Rating: {stars}",
            f"Target model: {target_model}",
            f"LoRA type: {lora_type}",
            f"Images: {len(imgs)}",
            f"Rank / Alpha: {rank} / {alpha}",
            f"Epochs: {epochs}",
            f"Learning rate: {lr}",
            f"Resolution: {resolution}",
            f"dataset.toml: {dataset_toml or 'not set'}",
        ]
        if problems:
            lines += ["", "## ❌ Fix first"] + [f"- {p}" for p in problems]
        if warnings:
            lines += ["", "## ⚠️ Review"] + [f"- {w}" for w in warnings]
        if not problems and not warnings:
            lines += ["", "✅ Ready to train."]
        elif not problems:
            lines += ["", "⚠️ Training can start, but review the warnings."]
        else:
            lines += ["", "❌ Fix errors first."]

    return "\n".join(lines)
