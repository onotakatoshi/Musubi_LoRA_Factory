from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline import IMAGE_EXTS


def rows_to_list(rows: Any) -> list[list[str]]:
    """Normalize Gradio Dataframe values.

    Gradio may pass a list of rows, a pandas DataFrame, or None depending on
    version/configuration. Keep the editor functions tolerant so the GUI does
    not crash during caption review.
    """
    if rows is None:
        return []
    if hasattr(rows, "values"):
        return [[str(cell) if cell is not None else "" for cell in row] for row in rows.values.tolist()]
    normalized: list[list[str]] = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append([str(row.get("image", "")), str(row.get("caption", ""))])
        else:
            cells = list(row)
            normalized.append([str(cells[0]) if len(cells) > 0 else "", str(cells[1]) if len(cells) > 1 else ""])
    return normalized


def load_caption_rows(dataset_dir: Path) -> list[list[str]]:
    if not dataset_dir.exists():
        return []
    rows: list[list[str]] = []
    for img in sorted(p for p in dataset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS):
        txt = img.with_suffix(".txt")
        caption = txt.read_text(encoding="utf-8").strip() if txt.exists() else ""
        rows.append([img.name, caption])
    return rows


def save_caption_rows(dataset_dir: Path, rows: Any) -> str:
    if not dataset_dir.exists():
        return f"NG: フォルダが存在しません: {dataset_dir}"
    saved = 0
    for row in rows_to_list(rows):
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


def bulk_replace_caption_rows(rows: Any, find_text: str, replace_text: str) -> list[list[str]]:
    normalized = rows_to_list(rows)
    if not find_text:
        return normalized
    updated: list[list[str]] = []
    for row in normalized:
        if not row or len(row) < 2:
            updated.append(row)
            continue
        updated.append([row[0], str(row[1]).replace(find_text, replace_text)])
    return updated


def remove_words_caption_rows(rows: Any, words_csv: str) -> list[list[str]]:
    normalized = rows_to_list(rows)
    words = [w.strip() for w in words_csv.split(",") if w.strip()]
    if not words:
        return normalized
    updated: list[list[str]] = []
    for row in normalized:
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
