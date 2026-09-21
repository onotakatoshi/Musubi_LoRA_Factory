from __future__ import annotations

from pathlib import Path
from typing import Any

from model_file_format import resolve_model_file

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_DIR = ROOT.parent / "models"
# Many users keep their weights only under ComfyUI. Searched after the main models dir.
COMFYUI_MODELS_DIR = ROOT.parent / "ComfyUI" / "models"

# Patterns are tried in order. Never list a *.safetensors.index.json manifest here:
# musubi-tuner cannot read one (see app/model_file_format.py). Split weights are
# addressed by their first shard, "-00001-of-0000N.safetensors".
CANDIDATES: dict[str, list[str]] = {
    "zimage_dit": ["z-image/Tongyi-MAI/Z-Image/transformer/diffusion_pytorch_model-00001-of-*.safetensors"],
    "zimage_vae": ["z-image/Tongyi-MAI/Z-Image/vae/diffusion_pytorch_model.safetensors"],
    "zimage_text_encoder": ["z-image/Tongyi-MAI/Z-Image/text_encoder/model-00001-of-*.safetensors"],

    "wan_vae": ["wan/Wan2.2-T2V-A14B/Wan2.1_VAE.pth", "wan/Wan2.2-T2V-A14B/*VAE*.pth"],
    "wan_t5": ["wan/Wan2.2-T2V-A14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-T2V-A14B/*t5*bf16*.pth"],
    "wan_dit": ["wan/Wan2.2-T2V-A14B/low_noise_model/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.2-T2V-A14B/low_noise_model/*.safetensors"],
    "wan_dit_high_noise": ["wan/Wan2.2-T2V-A14B/high_noise_model/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.2-T2V-A14B/high_noise_model/*.safetensors"],

    "wan22_i2v_vae": ["wan/Wan2.2-I2V-A14B/Wan2.1_VAE.pth", "wan/Wan2.2-I2V-A14B/*VAE*.pth"],
    "wan22_i2v_t5": ["wan/Wan2.2-I2V-A14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-I2V-A14B/*t5*bf16*.pth"],
    "wan22_i2v_dit": ["wan/Wan2.2-I2V-A14B/low_noise_model/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.2-I2V-A14B/low_noise_model/*.safetensors"],
    "wan22_i2v_dit_high_noise": ["wan/Wan2.2-I2V-A14B/high_noise_model/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.2-I2V-A14B/high_noise_model/*.safetensors"],

    "wan22_ti2v_vae": ["wan/Wan2.2-TI2V-5B/Wan2.2_VAE.pth", "wan/Wan2.2-TI2V-5B/*VAE*.pth"],
    "wan22_ti2v_t5": ["wan/Wan2.2-TI2V-5B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-TI2V-5B/*t5*bf16*.pth"],
    "wan22_ti2v_dit": ["wan/Wan2.2-TI2V-5B/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.2-TI2V-5B/*.safetensors"],

    "wan21_vae": ["wan/Wan2.1-T2V-14B/Wan2.1_VAE.pth", "wan/Wan2.1-T2V-14B/*VAE*.pth"],
    "wan21_t5": ["wan/Wan2.1-T2V-14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.1-T2V-14B/*t5*bf16*.pth"],
    "wan21_dit": ["wan/Wan2.1-T2V-14B/diffusion_pytorch_model-00001-of-*.safetensors", "wan/Wan2.1-T2V-14B/*.safetensors"],

    "qwen_image_vae": ["qwen/Qwen-Image/vae/diffusion_pytorch_model.safetensors", "qwen/Qwen-Image/vae/*.safetensors"],
    "qwen_image_text_encoder": ["qwen/Qwen-Image/text_encoder/model-00001-of-*.safetensors", "qwen/Qwen-Image/text_encoder/model.safetensors"],
    "qwen_image_dit": ["qwen/Qwen-Image/transformer/diffusion_pytorch_model-00001-of-*.safetensors", "qwen/Qwen-Image/transformer/*.safetensors"],

    # FLUX: musubi-tuner rejects the Diffusers subfolders ("The weights in the subfolder
    # are in Diffusers format and cannot be used"), so use the single files at repo root.
    # The text encoders must come from comfyanonymous/flux_text_encoders, not text_encoder*/.
    "flux_kontext_vae": ["flux/FLUX.1-Kontext-dev/ae.safetensors"],
    "flux_kontext_clip_l": ["flux/flux_text_encoders/clip_l.safetensors", "flux/FLUX.1-Kontext-dev/clip_l.safetensors"],
    "flux_kontext_t5": ["flux/flux_text_encoders/t5xxl_fp16.safetensors", "flux/flux_text_encoders/t5xxl_*.safetensors"],
    "flux_kontext_dit": ["flux/FLUX.1-Kontext-dev/flux1-kontext-dev.safetensors"],

    "flux2_dev_vae": ["flux/FLUX.2-dev/ae.safetensors"],
    "flux2_dev_text_encoder": ["flux/FLUX.2-dev/text_encoder/model-00001-of-*.safetensors"],
    "flux2_dev_dit": ["flux/FLUX.2-dev/flux2-dev.safetensors"],

    "flux2_klein_vae": ["flux/FLUX.2-klein-9B/ae.safetensors", "flux/FLUX.2-dev/ae.safetensors"],
    "flux2_klein_text_encoder": ["flux/FLUX.2-klein-9B/text_encoder/model-00001-of-*.safetensors"],
    "flux2_klein_dit": ["flux/FLUX.2-klein-9B/flux-2-klein-9b.safetensors", "flux/FLUX.2-klein-9B/flux2-klein*.safetensors"],

    "hv_vae": ["hunyuan-video/HunyuanVideo/hunyuan-video-t2v-720p/vae/pytorch_model.pt"],
    "hv_text_encoder1": ["hunyuan-video/Comfy-Org/HunyuanVideo_repackaged/split_files/text_encoders/llava_llama3_fp16.safetensors"],
    "hv_text_encoder2": ["hunyuan-video/Comfy-Org/HunyuanVideo_repackaged/split_files/text_encoders/clip_l.safetensors"],
    "hv_dit": ["hunyuan-video/HunyuanVideo/hunyuan-video-t2v-720p/transformers/mp_rank_00_model_states.pt"],

    "minimax_h3_dit": [
        "minimax-h3/Comfy-Org/MiniMax-H3/diffusion_models/minimax_h3_fl2va_bf16.safetensors",
        "minimax-h3/**/minimax_h3_fl2va_*.safetensors",
    ],
    "minimax_h3_text_encoder": [
        "minimax-h3/Comfy-Org/MiniMax-H3/text_encoders/qwen3vl_32b_minimax_h3_bf16.safetensors",
        "minimax-h3/**/qwen3vl_32b_minimax_h3_*.safetensors",
    ],
    "minimax_h3_video_vae": [
        "minimax-h3/Comfy-Org/MiniMax-H3/vae/minimax_h3_video_vae_fp16.safetensors",
        "minimax-h3/**/minimax_h3_video_vae_*.safetensors",
    ],
    "minimax_h3_audio_vae": [
        "minimax-h3/Comfy-Org/MiniMax-H3/vae/minimax_h3_audio_vae_fp32.safetensors",
        "minimax-h3/**/minimax_h3_audio_vae_*.safetensors",
    ],
}


# ComfyUI's flat layout, searched under COMFYUI_MODELS_DIR when the main models dir has
# no match. H3 names are listed explicitly rather than globbed because musubi-tuner
# rejects the fp8_scaled transformers, which a "minimax_h3_fl2va_*" glob would happily
# pick up. Order is best quality first.
COMFYUI_CANDIDATES: dict[str, list[str]] = {
    "minimax_h3_dit": [
        "diffusion_models/minimax_h3_fl2va_bf16.safetensors",
        "diffusion_models/minimax_h3_fl2va_pruned_bf16.safetensors",
        "diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors",
        "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    ],
    "minimax_h3_text_encoder": [
        "text_encoders/qwen3vl_32b_minimax_h3_bf16.safetensors",
        "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
        "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    ],
    "minimax_h3_video_vae": [
        "vae/minimax_h3_video_vae_fp16.safetensors",
        "vae/minimax_h3_video_vae_int8_convrot.safetensors",
    ],
    "minimax_h3_audio_vae": ["vae/minimax_h3_audio_vae_fp32.safetensors"],
}


def _setting_value(path: Path) -> str:
    try:
        return "../" + path.relative_to(ROOT.parent).as_posix()
    except ValueError:
        return path.as_posix()


def find_candidate(models_dir: Path, key: str) -> Path | None:
    """Best loadable file for ``key``, or None.

    The configured models dir wins; the ComfyUI tree is only consulted when nothing
    matched there.
    """
    patterns = CANDIDATES.get(key)
    if patterns:
        found = _find_first(models_dir, patterns)
        if found is not None:
            return found
    comfy_patterns = COMFYUI_CANDIDATES.get(key)
    comfy_root = COMFYUI_MODELS_DIR.expanduser()
    if comfy_patterns and comfy_root.is_dir():
        return _find_first(comfy_root, comfy_patterns)
    return None


def _find_first(models_dir: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        if any(ch in pattern for ch in "*?[]"):
            matches = sorted(p for p in models_dir.glob(pattern) if p.exists())
        else:
            candidate = models_dir / pattern
            matches = [candidate] if candidate.exists() else []
        for match in matches:
            resolved = resolve_model_file(match)
            if resolved is not None:
                return resolved
    return None


def autofill_model_paths(data: dict[str, Any], models_dir: Path | None = None, overwrite_empty_only: bool = True) -> dict[str, Any]:
    models_root = (models_dir or DEFAULT_MODELS_DIR).expanduser().resolve()
    model_paths = data.setdefault("model_paths", {})
    for key in CANDIDATES:
        current = str(model_paths.get(key, "") or "")
        if overwrite_empty_only and current:
            continue
        found = find_candidate(models_root, key)
        if found is not None:
            model_paths[key] = _setting_value(found)
    return data


def autofill_summary(before: dict[str, str], after: dict[str, str]) -> str:
    lines = []
    for key in sorted(set(CANDIDATES) | set(COMFYUI_CANDIDATES)):
        old = before.get(key, "") or ""
        new = after.get(key, "") or ""
        if new and new != old:
            lines.append(f"SET {key}: {new}")
    if not lines:
        return "No new model paths were detected."
    return "\n".join(lines)
