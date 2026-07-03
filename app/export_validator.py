from __future__ import annotations

from pathlib import Path


def validate_lora_for_export(lora_path: str | Path, comfyui_loras_dir: str | Path) -> str:
    src = Path(lora_path)
    dest_dir = Path(comfyui_loras_dir)
    lines = ["# Export Validation", ""]
    if not str(lora_path):
        lines.append("NG: LoRAファイルが未指定です。")
        return "\n".join(lines)
    if not src.exists():
        lines.append(f"NG: LoRAファイルが存在しません: {src}")
        return "\n".join(lines)
    if not src.is_file():
        lines.append(f"NG: LoRAパスがファイルではありません: {src}")
        return "\n".join(lines)
    if src.suffix.lower() != ".safetensors":
        lines.append(f"NG: .safetensors ファイルを指定してください: {src}")
        return "\n".join(lines)
    size_mb = src.stat().st_size / 1024 / 1024
    dest = dest_dir / src.name
    lines.append(f"OK: Source: {src}")
    lines.append(f"OK: Destination: {dest}")
    lines.append(f"Size: {size_mb:.1f} MB")
    lines.append(f"Overwrite: {'yes' if dest.exists() else 'no'}")
    lines.append("")
    lines.append("Next: 問題なければ ComfyUIへコピー を押してください。")
    return "\n".join(lines)
