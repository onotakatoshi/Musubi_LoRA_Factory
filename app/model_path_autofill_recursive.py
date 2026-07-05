from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_DIR = ROOT.parent / "models"

KEYS: dict[str, tuple[list[str], str]] = {
    "zimage_dit": (["Z-Image"], "dit"),
    "zimage_vae": (["Z-Image"], "vae"),
    "zimage_text_encoder": (["Z-Image"], "text"),
    "wan_vae": (["Wan2.2-T2V-A14B"], "vae"),
    "wan_t5": (["Wan2.2-T2V-A14B"], "t5"),
    "wan_dit": (["Wan2.2-T2V-A14B"], "low"),
    "wan_dit_high_noise": (["Wan2.2-T2V-A14B"], "high"),
    "wan22_i2v_vae": (["Wan2.2-I2V-A14B"], "vae"),
    "wan22_i2v_t5": (["Wan2.2-I2V-A14B"], "t5"),
    "wan22_i2v_dit": (["Wan2.2-I2V-A14B"], "low"),
    "wan22_i2v_dit_high_noise": (["Wan2.2-I2V-A14B"], "high"),
    "wan22_ti2v_vae": (["Wan2.2-TI2V-5B", "Wan2.2-TI2V-5B-Diffusers"], "vae"),
    "wan22_ti2v_t5": (["Wan2.2-TI2V-5B", "Wan2.2-TI2V-5B-Diffusers"], "t5"),
    "wan22_ti2v_dit": (["Wan2.2-TI2V-5B", "Wan2.2-TI2V-5B-Diffusers"], "dit"),
    "wan21_vae": (["Wan2.1-T2V-14B", "Wan2.1"], "vae"),
    "wan21_t5": (["Wan2.1-T2V-14B", "Wan2.1"], "t5"),
    "wan21_dit": (["Wan2.1-T2V-14B", "Wan2.1"], "dit"),
    "qwen_image_vae": (["Qwen-Image"], "vae"),
    "qwen_image_text_encoder": (["Qwen-Image"], "text"),
    "qwen_image_dit": (["Qwen-Image"], "dit"),
    "hv_vae": (["HunyuanVideo"], "vae"),
    "hv_text_encoder": (["HunyuanVideo"], "text"),
    "hv_dit": (["HunyuanVideo"], "dit"),
    "flux_kontext_vae": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "vae"),
    "flux_kontext_clip_l": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "text"),
    "flux_kontext_t5": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "t5"),
    "flux_kontext_dit": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "dit"),
    "flux2_dev_vae": (["FLUX.2-dev"], "vae"),
    "flux2_dev_text_encoder": (["FLUX.2-dev"], "text"),
    "flux2_dev_dit": (["FLUX.2-dev"], "dit"),
    "flux2_klein_vae": (["FLUX.2-klein"], "vae"),
    "flux2_klein_text_encoder": (["FLUX.2-klein"], "text"),
    "flux2_klein_dit": (["FLUX.2-klein"], "dit"),
}


def setting_value(path: Path) -> str:
    try:
        return "../" + path.relative_to(ROOT.parent).as_posix()
    except ValueError:
        return path.as_posix()


def find_root(models_dir: Path, hints: list[str]) -> Path | None:
    lowered = [h.lower() for h in hints]
    if not models_dir.exists():
        return None
    for p in sorted(x for x in models_dir.rglob("*") if x.is_dir()):
        name = p.name.lower()
        if any(h == name or h in name for h in lowered):
            return p
    return None


def wanted(path: Path, role: str) -> bool:
    s = path.as_posix().lower()
    n = path.name.lower()
    if role == "vae":
        return "vae" in s and path.suffix.lower() in {".pth", ".pt", ".safetensors"}
    if role == "t5":
        return ("t5" in s or "umt5" in s) and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "text":
        return any(x in s for x in ["text_encoder", "clip", "llm", "t5", "umt5"]) and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "low":
        return "low_noise" in s and (n.endswith(".index.json") or path.suffix.lower() == ".safetensors")
    if role == "high":
        return "high_noise" in s and (n.endswith(".index.json") or path.suffix.lower() == ".safetensors")
    if role == "dit":
        return not any(x in s for x in ["vae", "text_encoder", "clip", "t5", "umt5"]) and (n.endswith(".index.json") or path.suffix.lower() in {".safetensors", ".pt"})
    return False


def score(path: Path, role: str) -> tuple[int, str]:
    s = path.as_posix().lower()
    n = path.name.lower()
    v = 0
    if n.endswith(".index.json"):
        v += 80
    if "diffusion" in s or "transformer" in s:
        v += 50
    if role == "low" and "low_noise" in s:
        v += 100
    if role == "high" and "high_noise" in s:
        v += 100
    if role == "t5" and "bf16" in s:
        v += 20
    return (-v, s)


def find_role(root: Path, role: str) -> Path | None:
    files = [p for p in root.rglob("*") if p.is_file() and wanted(p, role)]
    if files:
        return sorted(files, key=lambda p: score(p, role))[0]
    if role == "low":
        dirs = sorted(p for p in root.rglob("*low*noise*") if p.is_dir())
        return dirs[0] if dirs else None
    if role == "high":
        dirs = sorted(p for p in root.rglob("*high*noise*") if p.is_dir())
        return dirs[0] if dirs else None
    if role == "dit":
        dirs = sorted(p for p in root.rglob("transformer") if p.is_dir())
        return dirs[0] if dirs else root
    return None


def detect_paths(models_dir: Path | None = None) -> dict[str, str]:
    root_dir = (models_dir or DEFAULT_MODELS_DIR).expanduser().resolve()
    found: dict[str, str] = {}
    for key, (hints, role) in KEYS.items():
        root = find_root(root_dir, hints)
        if root is None:
            continue
        path = find_role(root, role)
        if path is not None:
            found[key] = setting_value(path)
    return found


def autofill_model_paths(data: dict[str, Any], models_dir: Path | None = None, overwrite_empty_only: bool = True) -> dict[str, Any]:
    model_paths = data.setdefault("model_paths", {})
    for key, value in detect_paths(models_dir).items():
        if overwrite_empty_only and str(model_paths.get(key, "") or ""):
            continue
        model_paths[key] = value
    return data


def autofill_summary(before: dict[str, str], after: dict[str, str]) -> str:
    lines = []
    for key in sorted(KEYS):
        old = before.get(key, "") or ""
        new = after.get(key, "") or ""
        if new and new != old:
            lines.append(f"SET {key}: {new}")
    if not lines:
        return "No new model paths were detected under ~/models."
    return "\n".join(lines)
