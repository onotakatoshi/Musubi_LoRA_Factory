from __future__ import annotations

from pathlib import Path

from model_adapters import get_adapter
from model_registry import get_profile

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


def _status_dir(key: str, value: str) -> str:
    if not value:
        return f"❌ {key}: not set"
    p = Path(value)
    if not p.exists():
        return f"❌ {key}: not found: {value}"
    if not p.is_dir():
        return f"❌ {key}: not a directory: {value}"
    return f"✅ {key}: {value}"


def _status_file(key: str, value: str) -> str:
    if not value:
        return f"❌ {key}: not set"
    p = Path(value)
    if not p.exists():
        return f"❌ {key}: not found: {value}"
    if not p.is_file():
        return f"❌ {key}: not a file: {value}"
    return f"✅ {key}: {value}"


def validate_settings_paths(values: dict[str, str], profile_id: str = "z-image") -> str:
    profile = get_profile(profile_id)
    required_dirs = ["musubi_repo", "datasets_dir", "outputs_dir", "comfyui_loras_dir"]
    required_files = ["musubi_python"]
    lines = ["# Settings Validation", "", f"Profile: {profile.display_name}", ""]

    for key in required_dirs:
        lines.append(_status_dir(key, values.get(key, "")))
    for key in required_files:
        lines.append(_status_file(key, values.get(key, "")))

    try:
        adapter = get_adapter(profile.id)
        lines.append("")
        lines.append(f"## {profile.display_name} model paths")
        for key in adapter.required_setting_keys():
            lines.append(_status_file(key, values.get(key, "")))
        for key in adapter.optional_setting_keys():
            value = values.get(key, "")
            if value:
                lines.append(_status_file(key, value))
            else:
                lines.append(f"ℹ️ {key}: optional / not set")
    except NotImplementedError as exc:
        lines.append(f"❌ {exc}")

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
