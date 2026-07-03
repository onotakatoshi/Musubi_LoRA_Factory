from __future__ import annotations

from pathlib import Path

MODEL_EXTS = {".safetensors", ".pt", ".pth", ".bin"}


def _score_file(path: Path, keywords: list[str]) -> int:
    name = path.name.lower()
    score = 0
    for kw in keywords:
        if kw in name:
            score += 10
    if "fp8" in name:
        score += 2
    if "turbo" in name:
        score += 1
    return score


def _best_file(root: Path, keywords: list[str]) -> Path | None:
    if not root.exists():
        return None
    candidates = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in MODEL_EXTS]
    scored = [(p, _score_file(p, keywords)) for p in candidates]
    scored = [(p, s) for p, s in scored if s > 0]
    if not scored:
        return None
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[0][0]


def detect_zimage_files(model_dir: Path) -> dict[str, str]:
    """Detect likely Z-Image files from a selected model directory.

    This is intentionally conservative: it proposes candidates but does not
    overwrite settings unless the user clicks Apply in the GUI.
    """
    return {
        "zimage_dit": str(_best_file(model_dir, ["z_image", "z-image", "zimage", "dit", "transformer"]) or ""),
        "zimage_vae": str(_best_file(model_dir, ["ae", "vae"]) or ""),
        "zimage_text_encoder": str(_best_file(model_dir, ["text_encoder", "text-encoder", "qwen", "encoder"]) or ""),
    }


def validate_settings_paths(values: dict[str, str]) -> str:
    required_dirs = ["musubi_repo", "datasets_dir", "outputs_dir", "comfyui_loras_dir"]
    required_files = ["musubi_python", "zimage_dit", "zimage_vae", "zimage_text_encoder"]
    lines = ["# Settings Validation", ""]
    for key in required_dirs:
        value = values.get(key, "")
        if not value:
            lines.append(f"❌ {key}: not set")
        elif not Path(value).exists():
            lines.append(f"❌ {key}: not found: {value}")
        elif not Path(value).is_dir():
            lines.append(f"❌ {key}: not a directory: {value}")
        else:
            lines.append(f"✅ {key}: {value}")
    for key in required_files:
        value = values.get(key, "")
        if not value:
            lines.append(f"❌ {key}: not set")
        elif not Path(value).exists():
            lines.append(f"❌ {key}: not found: {value}")
        elif not Path(value).is_file():
            lines.append(f"❌ {key}: not a file: {value}")
        else:
            lines.append(f"✅ {key}: {value}")

    repo = Path(values.get("musubi_repo", ""))
    if repo.exists():
        src = repo / "src" / "musubi_tuner"
        if src.exists():
            lines.append(f"✅ musubi source: {src}")
        else:
            lines.append(f"❌ musubi source not found: {src}")

    text = "\n".join(lines)
    if "❌" in text:
        text += "\n\nResult: ❌ 不足があります。Browseで指定し直してください。"
    else:
        text += "\n\nResult: ✅ Settings looks good. Save Settingsしてください。"
    return text
