from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from model_file_format import is_first_shard, is_index_json, resolve_model_file

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_DIR = ROOT.parent / "models"


@dataclass(frozen=True)
class FileSpec:
    key: str
    names: tuple[str, ...]
    must_contain: tuple[str, ...] = ()
    prefer_contain: tuple[str, ...] = ()
    avoid_contain: tuple[str, ...] = ()


# ``names`` entries are fnmatch patterns matched against the file name. Never list a
# *.safetensors.index.json manifest: musubi-tuner loads split weights by the
# "-00001-of-0000N.safetensors" filename pattern and cannot read the manifest.
KNOWN_FILES: tuple[FileSpec, ...] = (
    FileSpec("zimage_vae", ("diffusion_pytorch_model.safetensors",), ("Z-Image", "vae")),
    FileSpec("zimage_text_encoder", ("model-00001-of-*.safetensors",), ("Z-Image", "text_encoder")),
    FileSpec("zimage_dit", ("diffusion_pytorch_model-00001-of-*.safetensors",), ("Z-Image", "transformer")),

    FileSpec("wan_vae", ("Wan2.1_VAE.pth",), ("Wan2.2-T2V-A14B",)),
    FileSpec("wan_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-T2V-A14B",)),
    FileSpec("wan_dit", ("diffusion_pytorch_model-00001-of-*.safetensors",), ("Wan2.2-T2V-A14B", "low_noise_model")),
    FileSpec("wan_dit_high_noise", ("diffusion_pytorch_model-00001-of-*.safetensors",), ("Wan2.2-T2V-A14B", "high_noise_model")),

    FileSpec("wan22_i2v_vae", ("Wan2.1_VAE.pth",), ("Wan2.2-I2V-A14B",)),
    FileSpec("wan22_i2v_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-I2V-A14B",)),
    FileSpec("wan22_i2v_dit", ("diffusion_pytorch_model-00001-of-*.safetensors",), ("Wan2.2-I2V-A14B", "low_noise_model")),
    FileSpec("wan22_i2v_dit_high_noise", ("diffusion_pytorch_model-00001-of-*.safetensors",), ("Wan2.2-I2V-A14B", "high_noise_model")),

    FileSpec("wan22_ti2v_vae", ("Wan2.2_VAE.pth", "Wan2.1_VAE.pth"), ("Wan2.2-TI2V-5B",)),
    FileSpec("wan22_ti2v_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-TI2V-5B",)),
    FileSpec("wan22_ti2v_dit", ("diffusion_pytorch_model-00001-of-*.safetensors", "diffusion_pytorch_model.safetensors"), ("Wan2.2-TI2V-5B",)),

    FileSpec("wan21_vae", ("Wan2.1_VAE.pth",), ("Wan2.1-T2V-14B",)),
    FileSpec("wan21_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.1-T2V-14B",)),
    FileSpec("wan21_dit", ("diffusion_pytorch_model-00001-of-*.safetensors", "diffusion_pytorch_model.safetensors"), ("Wan2.1-T2V-14B",)),

    FileSpec("qwen_image_vae", ("diffusion_pytorch_model.safetensors",), ("Qwen-Image", "vae")),
    FileSpec("qwen_image_text_encoder", ("model-00001-of-*.safetensors", "model.safetensors"), ("Qwen-Image", "text_encoder")),
    FileSpec("qwen_image_dit", ("diffusion_pytorch_model-00001-of-*.safetensors", "diffusion_pytorch_model.safetensors"), ("Qwen-Image", "transformer")),

    # FLUX: the Diffusers subfolders (transformer/, vae/, text_encoder*/) are rejected by
    # musubi-tuner, so only the repo-root single files and the ComfyUI text encoders count.
    FileSpec("flux_kontext_vae", ("ae.safetensors",), ("FLUX.1-Kontext",)),
    FileSpec("flux_kontext_clip_l", ("clip_l.safetensors",), ("flux",), (), ("HunyuanVideo",)),
    FileSpec("flux_kontext_t5", ("t5xxl_fp16.safetensors", "t5xxl_*.safetensors"), ("flux",)),
    FileSpec("flux_kontext_dit", ("flux1-kontext-dev.safetensors",), ("FLUX.1-Kontext",)),

    FileSpec("flux2_dev_vae", ("ae.safetensors",), ("FLUX.2-dev",)),
    FileSpec("flux2_dev_text_encoder", ("model-00001-of-*.safetensors",), ("FLUX.2-dev", "text_encoder")),
    FileSpec("flux2_dev_dit", ("flux2-dev.safetensors",), ("FLUX.2-dev",)),

    # klein ships no ae.safetensors of its own; musubi-tuner says to reuse the FLUX.2-dev one.
    FileSpec("flux2_klein_vae", ("ae.safetensors",), ("flux",), ("FLUX.2-klein", "FLUX.2"), ("FLUX.1",)),
    FileSpec("flux2_klein_text_encoder", ("model-00001-of-*.safetensors",), ("FLUX.2-klein", "text_encoder")),
    FileSpec("flux2_klein_dit", ("flux-2-klein-9b.safetensors", "flux2-klein*.safetensors"), ("FLUX.2-klein",)),

    FileSpec("hv_vae", ("pytorch_model.pt", "diffusion_pytorch_model.safetensors"), ("HunyuanVideo", "vae")),
    FileSpec("hv_text_encoder1", ("llava_llama3_fp16.safetensors",), ("HunyuanVideo_repackaged", "text_encoders")),
    FileSpec("hv_text_encoder2", ("clip_l.safetensors",), ("HunyuanVideo_repackaged", "text_encoders")),
    FileSpec("hv_dit", ("mp_rank_00_model_states.pt", "diffusion_pytorch_model-00001-of-*.safetensors", "diffusion_pytorch_model.safetensors"), ("HunyuanVideo",), ("transformer", "transformers"), ("vae", "text_encoder")),

    FileSpec("minimax_h3_dit", ("minimax_h3_fl2va_bf16.safetensors", "minimax_h3_fl2va_*.safetensors", "minimax_h3_ref2va_*.safetensors"), ("MiniMax-H3",)),
    FileSpec("minimax_h3_text_encoder", ("qwen3vl_32b_minimax_h3_bf16.safetensors", "qwen3vl_32b_minimax_h3_*.safetensors"), ("MiniMax-H3",)),
    FileSpec("minimax_h3_video_vae", ("minimax_h3_video_vae_fp16.safetensors", "minimax_h3_video_vae_*.safetensors"), ("MiniMax-H3",)),
    FileSpec("minimax_h3_audio_vae", ("minimax_h3_audio_vae_fp32.safetensors", "minimax_h3_audio_vae_*.safetensors"), ("MiniMax-H3",)),
)


def setting_value(path: Path) -> str:
    try:
        return "../" + path.resolve().relative_to(ROOT.parent.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _score(path: Path, spec: FileSpec, name_rank: int) -> tuple[int, int, str]:
    text = path.as_posix().lower()
    score = 0
    for token in spec.prefer_contain:
        if token.lower() in text:
            score += 10
    for token in spec.avoid_contain:
        if token.lower() in text:
            score -= 20
    if is_first_shard(path):
        score += 5
    return (name_rank, -score, text)


def _find_one(models_dir: Path, spec: FileSpec) -> Path | None:
    if not models_dir.exists():
        return None
    matches: list[tuple[Path, int]] = []
    required = tuple(token.lower() for token in spec.must_contain)
    for path in models_dir.rglob("*"):
        if not path.is_file() or is_index_json(path):
            continue
        name = path.name.lower()
        rank = next((i for i, pattern in enumerate(spec.names) if fnmatch.fnmatch(name, pattern.lower())), None)
        if rank is None:
            continue
        text = path.as_posix().lower()
        if all(token.lower() in text for token in required):
            matches.append((path, rank))
    if not matches:
        return None
    best = sorted(matches, key=lambda item: _score(item[0], spec, item[1]))[0][0]
    return resolve_model_file(best)


def search_known_model_filenames(models_dir: Path | None = None) -> dict[str, str]:
    root = (models_dir or DEFAULT_MODELS_DIR).expanduser().resolve()
    found: dict[str, str] = {}
    for spec in KNOWN_FILES:
        path = _find_one(root, spec)
        if path is not None:
            found[spec.key] = setting_value(path)
    return found


def apply_known_filename_search(data: dict[str, Any], models_dir: Path | None = None, overwrite: bool = True) -> dict[str, Any]:
    model_paths = data.setdefault("model_paths", {})
    for key, value in search_known_model_filenames(models_dir).items():
        if not overwrite and str(model_paths.get(key, "") or ""):
            continue
        model_paths[key] = value
    return data


def search_summary(before: dict[str, str], after: dict[str, str]) -> str:
    lines: list[str] = []
    for spec in KNOWN_FILES:
        old = before.get(spec.key, "") or ""
        new = after.get(spec.key, "") or ""
        if new and old != new:
            names = ", ".join(spec.names)
            lines.append(f"SET {spec.key}: {new}  <= {names}")
    return "\n".join(lines) if lines else "No matching known filenames were found under ~/models."
