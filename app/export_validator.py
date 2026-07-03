from __future__ import annotations

from pathlib import Path


def _ng(lines: list[str], message: str) -> str:
    lines.append(message)
    lines.append("")
    lines.append("Result: NG")
    return "\n".join(lines)


def validate_lora_for_export(lora_path: str | Path, comfyui_loras_dir: str | Path) -> str:
    src = Path(lora_path)
    dest_dir = Path(comfyui_loras_dir)
    lines = ["# Export Validation", ""]
    if not str(lora_path):
        return _ng(lines, "NG: LoRAファイルが未指定です。")
    if not src.exists():
        return _ng(lines, f"NG: LoRAファイルが存在しません: {src}")
    if not src.is_file():
        return _ng(lines, f"NG: LoRAパスがファイルではありません: {src}")
    if src.suffix.lower() != ".safetensors":
        return _ng(lines, f"NG: .safetensors ファイルを指定してください: {src}")
    if not dest_dir.exists():
        return _ng(lines, f"NG: ComfyUI LoRAフォルダが存在しません: {dest_dir}")
    if not dest_dir.is_dir():
        return _ng(lines, f"NG: ComfyUI LoRAパスがフォルダではありません: {dest_dir}")
    size_mb = src.stat().st_size / 1024 / 1024
    dest = dest_dir / src.name
    lines.append(f"OK: Source: {src}")
    lines.append(f"OK: Destination: {dest}")
    lines.append(f"Size: {size_mb:.1f} MB")
    lines.append(f"Overwrite: {'yes' if dest.exists() else 'no'}")
    lines.append("")
    lines.append("Result: OK")
    lines.append("Next: 問題なければ ComfyUIへコピー を押してください。")
    return "\n".join(lines)
