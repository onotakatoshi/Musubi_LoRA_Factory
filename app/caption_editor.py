from __future__ import annotations

from pathlib import Path

from pipeline import IMAGE_EXTS


def load_caption_rows(dataset_dir: Path) -> list[list[str]]:
    if not dataset_dir.exists():
        return []
    rows: list[list[str]] = []
    for img in sorted(p for p in dataset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS):
        txt = img.with_suffix(".txt")
        caption = txt.read_text(encoding="utf-8").strip() if txt.exists() else ""
        rows.append([img.name, caption])
    return rows


def save_caption_rows(dataset_dir: Path, rows: list[list[str]]) -> str:
    if not dataset_dir.exists():
        return f"NG: フォルダが存在しません: {dataset_dir}"
    saved = 0
    for row in rows:
        if not row or len(row) < 2:
            continue
        image_name = str(row[0]).strip()
        caption = str(row[1]).strip()
        if not image_name:
            continue
        img_path = dataset_dir / image_name
        if img_path.suffix.lower() not in IMAGE_EXTS:
            continue
        img_path.with_suffix(".txt").write_text(caption + "\n", encoding="utf-8")
        saved += 1
    return f"保存完了: {saved}件"


def bulk_replace_caption_rows(rows: list[list[str]], find_text: str, replace_text: str) -> list[list[str]]:
    if not find_text:
        return rows
    updated: list[list[str]] = []
    for row in rows:
        if not row or len(row) < 2:
            updated.append(row)
            continue
        updated.append([row[0], str(row[1]).replace(find_text, replace_text)])
    return updated


def remove_words_caption_rows(rows: list[list[str]], words_csv: str) -> list[list[str]]:
    words = [w.strip() for w in words_csv.split(",") if w.strip()]
    if not words:
        return rows
    updated: list[list[str]] = []
    for row in rows:
        if not row or len(row) < 2:
            updated.append(row)
            continue
        tags = [t.strip() for t in str(row[1]).split(",") if t.strip()]
        filtered = []
        for tag in tags:
            lower = tag.lower()
            if any(w.lower() in lower for w in words):
                continue
            filtered.append(tag)
        updated.append([row[0], ", ".join(filtered)])
    return updated
