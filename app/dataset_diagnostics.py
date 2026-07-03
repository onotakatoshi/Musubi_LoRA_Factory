from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from PIL import Image

from pipeline import IMAGE_EXTS, image_files


def _file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def diagnose_dataset(dataset_dir: Path, lang: str = "日本語") -> str:
    ja = lang != "English"
    if not dataset_dir.exists():
        return f"❌ フォルダが存在しません: {dataset_dir}" if ja else f"❌ Folder not found: {dataset_dir}"

    imgs = image_files(dataset_dir)
    if not imgs:
        return "❌ 画像が見つかりません。png/jpg/jpeg/webp を入れてください。" if ja else "❌ No images found. Add png/jpg/jpeg/webp files."

    ext_counts: Counter[str] = Counter()
    size_counts: Counter[str] = Counter()
    aspect_counts: Counter[str] = Counter()
    missing_caption: list[str] = []
    small_images: list[str] = []
    broken_images: list[str] = []
    duplicate_groups: dict[str, list[str]] = {}

    for img in imgs:
        ext_counts[img.suffix.lower()] += 1
        if not img.with_suffix(".txt").exists():
            missing_caption.append(img.name)
        try:
            with Image.open(img) as im:
                w, h = im.width, im.height
                size_counts[f"{w}x{h}"] += 1
                if w == h:
                    aspect_counts["1:1"] += 1
                else:
                    aspect_counts[f"{w}:{h}"] += 1
                if min(w, h) < 512:
                    small_images.append(f"{img.name} ({w}x{h})")
            digest = _file_hash(img)
            duplicate_groups.setdefault(digest, []).append(img.name)
        except Exception as exc:
            broken_images.append(f"{img.name}: {exc}")

    duplicates = [names for names in duplicate_groups.values() if len(names) > 1]
    caption_count = len(imgs) - len(missing_caption)

    if ja:
        lines = [
            "# Dataset診断",
            "",
            f"✅ 画像数: {len(imgs)}",
            f"✅ captionあり: {caption_count}",
            f"{'⚠️' if missing_caption else '✅'} caption未作成: {len(missing_caption)}",
            f"{'⚠️' if small_images else '✅'} 512px未満の画像: {len(small_images)}",
            f"{'⚠️' if duplicates else '✅'} 完全重複の疑い: {len(duplicates)}グループ",
            f"{'❌' if broken_images else '✅'} 読み込み失敗: {len(broken_images)}",
            "",
            "## 拡張子",
        ]
    else:
        lines = [
            "# Dataset Diagnostics",
            "",
            f"✅ Images: {len(imgs)}",
            f"✅ Captions found: {caption_count}",
            f"{'⚠️' if missing_caption else '✅'} Missing captions: {len(missing_caption)}",
            f"{'⚠️' if small_images else '✅'} Images under 512px: {len(small_images)}",
            f"{'⚠️' if duplicates else '✅'} Exact duplicate groups: {len(duplicates)}",
            f"{'❌' if broken_images else '✅'} Broken images: {len(broken_images)}",
            "",
            "## Extensions",
        ]

    lines += [f"- {ext}: {count}" for ext, count in sorted(ext_counts.items())]
    lines.append("\n## 解像度" if ja else "\n## Resolutions")
    lines += [f"- {size}: {count}" for size, count in size_counts.most_common(20)]
    lines.append("\n## アスペクト比" if ja else "\n## Aspect ratios")
    lines += [f"- {aspect}: {count}" for aspect, count in aspect_counts.most_common(20)]

    def add_samples(title_ja: str, title_en: str, items: list[str]) -> None:
        if items:
            lines.append(f"\n## {title_ja if ja else title_en}")
            lines.extend(f"- {item}" for item in items[:20])
            if len(items) > 20:
                lines.append(f"...他 {len(items) - 20} 件" if ja else f"...and {len(items) - 20} more")

    add_samples("caption未作成サンプル", "Missing caption samples", missing_caption)
    add_samples("512px未満サンプル", "Small image samples", small_images)
    add_samples("読み込み失敗", "Broken images", broken_images)

    if duplicates:
        lines.append("\n## 完全重複の疑い" if ja else "\n## Exact duplicate candidates")
        for group in duplicates[:10]:
            lines.append("- " + ", ".join(group))

    if not missing_caption and not small_images and not broken_images:
        lines.append("\n次: Configタブで dataset.toml を作成してください。" if ja else "\nNext: Build dataset.toml in the Config tab.")
    else:
        lines.append("\n次: 上の⚠️/❌を確認してから進んでください。" if ja else "\nNext: Review the ⚠️/❌ items before continuing.")

    return "\n".join(lines)
