from __future__ import annotations

from pathlib import Path
from typing import Any

from model_file_format import is_first_shard, is_index_json, resolve_model_file
from model_path_autofill import find_candidate

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
    "hv_vae": (["hunyuan-video-t2v-720p"], "vae"),
    "hv_text_encoder1": (["HunyuanVideo_repackaged"], "text_llava"),
    "hv_text_encoder2": (["HunyuanVideo_repackaged"], "text_clip"),
    "hv_dit": (["hunyuan-video-t2v-720p"], "dit"),
    "flux_kontext_vae": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "vae"),
    "flux_kontext_clip_l": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "text"),
    "flux_kontext_t5": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "t5"),
    "flux_kontext_dit": (["FLUX.1-Kontext-dev", "FLUX.1-Kontext"], "dit"),
    "flux2_dev_vae": (["FLUX.2-dev"], "vae"),
    "flux2_dev_text_encoder": (["FLUX.2-dev"], "text"),
    "flux2_dev_dit": (["FLUX.2-dev"], "dit"),
    "flux2_klein_vae": (["FLUX.2-klein-9B"], "vae"),
    "flux2_klein_text_encoder": (["FLUX.2-klein-9B"], "text"),
    "flux2_klein_dit": (["FLUX.2-klein-9B"], "dit"),
    "minimax_h3_dit": (["MiniMax-H3", "minimax-h3"], "dit"),
    "minimax_h3_text_encoder": (["MiniMax-H3", "minimax-h3"], "text"),
    "minimax_h3_video_vae": (["MiniMax-H3", "minimax-h3"], "video_vae"),
    "minimax_h3_audio_vae": (["MiniMax-H3", "minimax-h3"], "audio_vae"),
    "krea2_dit": (["Krea-2", "krea2"], "dit"),
    "krea2_vae": (["Krea-2", "krea2"], "vae"),
    "krea2_text_encoder": (["Krea-2", "krea2"], "text"),
}


# FLUX ships both a usable single file at the repo root and an unusable Diffusers copy
# in a subfolder, and its text encoders come from a different repository entirely. A
# recursive "looks like a text encoder" scan picks the wrong one every time, so these
# keys are resolved from the exact table only.
EXACT_ONLY = {key for key in KEYS if key.startswith(("flux_kontext_", "flux2_"))}


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
        if ".cache" in p.parts:
            continue
        name = p.name.lower()
        if any(h == name or h in name for h in lowered):
            return p
    return None


def wanted(path: Path, role: str) -> bool:
    s = path.as_posix().lower()
    n = path.name.lower()
    if is_index_json(path):
        return False  # musubi-tuner cannot read a safetensors index manifest
    if role == "vae":
        return "vae" in s and path.suffix.lower() in {".pth", ".pt", ".safetensors"}
    if role == "video_vae":
        return "video_vae" in n and path.suffix.lower() == ".safetensors"
    if role == "audio_vae":
        return "audio_vae" in n and path.suffix.lower() == ".safetensors"
    if role == "t5":
        return ("t5" in s or "umt5" in s or "text_encoder_2" in s) and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "text_llava":
        return "llava" in n and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "text_clip":
        return ("clip_l" in n or "clip" in n) and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "text":
        return any(x in s for x in ["text_encoder", "clip", "llm", "t5", "umt5"]) and path.suffix.lower() in {".pth", ".pt", ".safetensors", ".bin"}
    if role == "low":
        return "low_noise" in s and path.suffix.lower() == ".safetensors"
    if role == "high":
        return "high_noise" in s and path.suffix.lower() == ".safetensors"
    if role == "dit":
        return not any(x in s for x in ["vae", "text_encoder", "clip", "t5", "umt5"]) and path.suffix.lower() in {".safetensors", ".pt"}
    return False


def score(path: Path, role: str) -> tuple[int, str]:
    s = path.as_posix().lower()
    n = path.name.lower()
    v = 0
    if is_first_shard(path):
        v += 80
    elif "-of-" in n:
        v -= 200  # a middle shard is never the path to pass to musubi-tuner
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
    files = [p for p in root.rglob("*") if p.is_file() and ".cache" not in p.parts and wanted(p, role)]
    if files:
        return sorted(files, key=lambda p: score(p, role))[0]
    if role == "low":
        dirs = sorted(p for p in root.rglob("*low*noise*") if p.is_dir())
        return resolve_model_file(dirs[0]) if dirs else None
    if role == "high":
        dirs = sorted(p for p in root.rglob("*high*noise*") if p.is_dir())
        return resolve_model_file(dirs[0]) if dirs else None
    if role == "dit":
        dirs = sorted(p for p in root.rglob("transformer") if p.is_dir())
        return resolve_model_file(dirs[0] if dirs else root)
    return None


def detect_paths(models_dir: Path | None = None) -> dict[str, str]:
    root_dir = (models_dir or DEFAULT_MODELS_DIR).expanduser().resolve()
    found: dict[str, str] = {}
    for key, (hints, role) in KEYS.items():
        # Known repo layouts are matched exactly first; the recursive scan below is the
        # fallback for models the user laid out differently.
        exact = find_candidate(root_dir, key)
        if exact is not None:
            found[key] = setting_value(exact)
            continue
        if key in EXACT_ONLY:
            continue
        root = find_root(root_dir, hints)
        if root is None:
            continue
        path = find_role(root, role)
        if path is None:
            continue
        resolved = resolve_model_file(path)
        if resolved is not None:
            found[key] = setting_value(resolved)
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
