from __future__ import annotations

from pathlib import Path

from pipeline import IMAGE_EXTS
from runner import validate_command_preview


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
        lines.append("次: Caption編集タブでcaptionを作成・保存してください。")
    else:
        lines.append("✅ caption: 全画像分あります。")
        lines.append("次: 設定生成タブで dataset.toml を作成してください。")
    return "\n".join(lines)


def config_status(dataset_toml: str) -> str:
    if not dataset_toml:
        return "❌ dataset.toml が未作成です。設定生成タブで dataset.toml を作成してください。"
    path = Path(dataset_toml)
    if not path.exists():
        return f"❌ dataset.toml が存在しません: {path}"
    return "✅ dataset.toml があります。次: 学習タブで 事前チェック を押してください。"


def train_ready_status(command_preview: str) -> str:
    validation = validate_command_preview(command_preview)
    if validation.startswith("NG:"):
        return validation + "\n\n次: コマンド確認を押し、NG表示があれば設定・dataset.toml・モデルパスを直してください。"
    return validation + "\n\n次: Latent Cache → Text Cache → 学習実行 の順に押してください。"
