from __future__ import annotations

from pathlib import Path


def find_latest_lora(output_dir: str | Path, output_name: str = "") -> Path | None:
    root = Path(output_dir)
    if not root.exists():
        return None
    candidates = [p for p in root.rglob("*.safetensors") if p.is_file()]
    if output_name:
        named = [p for p in candidates if output_name in p.stem]
        if named:
            candidates = named
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def output_summary(output_dir: str | Path, output_name: str = "") -> str:
    latest = find_latest_lora(output_dir, output_name)
    if latest is None:
        return "NG: LoRA .safetensors がまだ見つかりません。学習ログと出力フォルダを確認してください。"
    size_mb = latest.stat().st_size / 1024 / 1024
    return f"OK: LoRAを検出しました。\n{latest}\nSize: {size_mb:.1f} MB"
