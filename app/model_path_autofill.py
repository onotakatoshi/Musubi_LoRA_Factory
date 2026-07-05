from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_DIR = ROOT.parent / "models"

CANDIDATES: dict[str, list[str]] = {
    "zimage_dit": ["z-image/Tongyi-MAI/Z-Image/transformer/diffusion_pytorch_model-00001-of-00002.safetensors"],
    "zimage_vae": ["z-image/Tongyi-MAI/Z-Image/vae/diffusion_pytorch_model.safetensors"],
    "zimage_text_encoder": ["z-image/Tongyi-MAI/Z-Image/text_encoder/model-00001-of-00003.safetensors"],

    "wan_vae": ["wan/Wan2.2-T2V-A14B/Wan2.1_VAE.pth", "wan/Wan2.2-T2V-A14B/*VAE*.pth"],
    "wan_t5": ["wan/Wan2.2-T2V-A14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-T2V-A14B/*t5*bf16*.pth"],
    "wan_dit": ["wan/Wan2.2-T2V-A14B/low_noise_model/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.2-T2V-A14B/low_noise_model/*.index.json"],
    "wan_dit_high_noise": ["wan/Wan2.2-T2V-A14B/high_noise_model/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.2-T2V-A14B/high_noise_model/*.index.json"],

    "wan22_i2v_vae": ["wan/Wan2.2-I2V-A14B/Wan2.1_VAE.pth", "wan/Wan2.2-I2V-A14B/*VAE*.pth"],
    "wan22_i2v_t5": ["wan/Wan2.2-I2V-A14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-I2V-A14B/*t5*bf16*.pth"],
    "wan22_i2v_dit": ["wan/Wan2.2-I2V-A14B/low_noise_model/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.2-I2V-A14B/low_noise_model/*.index.json"],
    "wan22_i2v_dit_high_noise": ["wan/Wan2.2-I2V-A14B/high_noise_model/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.2-I2V-A14B/high_noise_model/*.index.json"],

    "wan22_ti2v_vae": ["wan/Wan2.2-TI2V-5B/Wan2.2_VAE.pth", "wan/Wan2.2-TI2V-5B/Wan2.1_VAE.pth", "wan/Wan2.2-TI2V-5B/*VAE*.pth"],
    "wan22_ti2v_t5": ["wan/Wan2.2-TI2V-5B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.2-TI2V-5B/*t5*bf16*.pth"],
    "wan22_ti2v_dit": ["wan/Wan2.2-TI2V-5B/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.2-TI2V-5B/*.index.json"],

    "wan21_vae": ["wan/Wan2.1-T2V-14B/Wan2.1_VAE.pth", "wan/Wan2.1-T2V-14B/*VAE*.pth"],
    "wan21_t5": ["wan/Wan2.1-T2V-14B/models_t5_umt5-xxl-enc-bf16.pth", "wan/Wan2.1-T2V-14B/*t5*bf16*.pth"],
    "wan21_dit": ["wan/Wan2.1-T2V-14B/diffusion_pytorch_model.safetensors.index.json", "wan/Wan2.1-T2V-14B/*.index.json", "wan/Wan2.1-T2V-14B/*.safetensors"],

    "qwen_image_vae": ["qwen/Qwen-Image/vae/diffusion_pytorch_model.safetensors", "qwen/Qwen-Image/vae/*.safetensors"],
    "qwen_image_text_encoder": ["qwen/Qwen-Image/text_encoder/model.safetensors", "qwen/Qwen-Image/text_encoder/*.safetensors"],
    "qwen_image_dit": ["qwen/Qwen-Image/transformer/diffusion_pytorch_model.safetensors.index.json", "qwen/Qwen-Image/transformer/*.index.json", "qwen/Qwen-Image/transformer/*.safetensors"],

    "flux_kontext_vae": ["flux/FLUX.1-Kontext-dev/vae/diffusion_pytorch_model.safetensors", "flux/FLUX.1-Kontext-dev/vae/*.safetensors"],
    "flux_kontext_clip_l": ["flux/FLUX.1-Kontext-dev/text_encoder/model.safetensors", "flux/FLUX.1-Kontext-dev/text_encoder/*.safetensors"],
    "flux_kontext_t5": ["flux/FLUX.1-Kontext-dev/text_encoder_2/model.safetensors", "flux/FLUX.1-Kontext-dev/text_encoder_2/*.safetensors"],
    "flux_kontext_dit": ["flux/FLUX.1-Kontext-dev/transformer/diffusion_pytorch_model.safetensors.index.json", "flux/FLUX.1-Kontext-dev/transformer/*.index.json", "flux/FLUX.1-Kontext-dev/transformer/*.safetensors"],

    "flux2_dev_vae": ["flux/FLUX.2-dev/vae/diffusion_pytorch_model.safetensors", "flux/FLUX.2-dev/vae/*.safetensors"],
    "flux2_dev_text_encoder": ["flux/FLUX.2-dev/text_encoder_2/model.safetensors", "flux/FLUX.2-dev/text_encoder_2/*.safetensors", "flux/FLUX.2-dev/text_encoder/*.safetensors"],
    "flux2_dev_dit": ["flux/FLUX.2-dev/transformer/diffusion_pytorch_model.safetensors.index.json", "flux/FLUX.2-dev/transformer/*.index.json", "flux/FLUX.2-dev/transformer/*.safetensors"],

    "flux2_klein_vae": ["flux/FLUX.2-klein/vae/diffusion_pytorch_model.safetensors", "flux/FLUX.2-klein/vae/*.safetensors"],
    "flux2_klein_text_encoder": ["flux/FLUX.2-klein/text_encoder_2/model.safetensors", "flux/FLUX.2-klein/text_encoder_2/*.safetensors", "flux/FLUX.2-klein/text_encoder/*.safetensors"],
    "flux2_klein_dit": ["flux/FLUX.2-klein/transformer/diffusion_pytorch_model.safetensors.index.json", "flux/FLUX.2-klein/transformer/*.index.json", "flux/FLUX.2-klein/transformer/*.safetensors"],
}


def _setting_value(path: Path) -> str:
    try:
        return "../" + path.relative_to(ROOT.parent).as_posix()
    except ValueError:
        return path.as_posix()


def _find_first(models_dir: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        if any(ch in pattern for ch in "*?[]"):
            matches = sorted(p for p in models_dir.glob(pattern) if p.exists())
            if matches:
                return matches[0]
        else:
            candidate = models_dir / pattern
            if candidate.exists():
                return candidate
    return None


def autofill_model_paths(data: dict[str, Any], models_dir: Path | None = None, overwrite_empty_only: bool = True) -> dict[str, Any]:
    models_root = (models_dir or DEFAULT_MODELS_DIR).expanduser().resolve()
    model_paths = data.setdefault("model_paths", {})
    for key, patterns in CANDIDATES.items():
        current = str(model_paths.get(key, "") or "")
        if overwrite_empty_only and current:
            continue
        found = _find_first(models_root, patterns)
        if found is not None:
            model_paths[key] = _setting_value(found)
    return data


def autofill_summary(before: dict[str, str], after: dict[str, str]) -> str:
    lines = []
    for key in sorted(CANDIDATES):
        old = before.get(key, "") or ""
        new = after.get(key, "") or ""
        if new and new != old:
            lines.append(f"SET {key}: {new}")
    if not lines:
        return "No new model paths were detected."
    return "\n".join(lines)
