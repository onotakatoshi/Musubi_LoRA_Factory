from __future__ import annotations

from pathlib import Path

from pipeline import IMAGE_EXTS


def dataset_status(dataset_dir: str) -> str:
    if not dataset_dir:
        return "❌ Dataset folder が未入力です。"
    path = Path(dataset_dir)
    if not path.exists():
        return f"❌ Dataset folder が存在しません: {path}"
    images = sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not images:
        return "❌ 画像が見つかりません。png/jpg/jpeg/webp を入れてください。"
    captions = [p.with_suffix(".txt") for p in images]
    missing = [p for p in captions if not p.exists()]
    lines = ["# Dataset Status", "", f"✅ 画像: {len(images)}枚"]
    if missing:
        lines.append(f"⚠️ caption未作成: {len(missing)}件")
        lines.append("次: Generate Captions または Caption Editor でcaptionを作成してください。")
    else:
        lines.append("✅ caption: 全画像分あります。")
        lines.append("次: Configタブで Build dataset.toml を押してください。")
    return "\n".join(lines)


def config_status(dataset_toml: str) -> str:
    if not dataset_toml:
        return "❌ dataset.toml が未作成です。Configタブで Build dataset.toml を押してください。"
    path = Path(dataset_toml)
    if not path.exists():
        return f"❌ dataset.toml が存在しません: {path}"
    return "✅ dataset.toml があります。次: Trainタブで Preflight Check を押してください。"


def train_ready_status(command_preview: str) -> str:
    if not command_preview:
        return "❌ Command Preview がありません。まず Preview Commands を押してください。"
    required = ["# 1. Latent cache", "# 2. Text encoder cache", "# 3. Train LoRA"]
    missing = [item for item in required if item not in command_preview]
    if missing:
        return "❌ Command Preview が不完全です。Preview Commandsを押し直してください。\n" + "\n".join(missing)
    return "✅ 実行準備OKです。Run 1 → Run 2 → Run 3 の順に押してください。"
