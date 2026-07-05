#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import toml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("toml is required. Run scripts/setup.sh first.") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = ROOT / "configs" / "settings.toml"
DEFAULT_EXAMPLE = ROOT / "configs" / "settings.example.toml"
DEFAULT_MODELS_DIR = Path.home() / "models"

MODEL_PATH_CANDIDATES: dict[str, list[str]] = {
    # Z-Image / Z-Image-Turbo
    "zimage_dit": ["z-image/Tongyi-MAI/Z-Image/transformer/diffusion_pytorch_model-00001-of-00002.safetensors"],
    "zimage_vae": ["z-image/Tongyi-MAI/Z-Image/vae/diffusion_pytorch_model.safetensors"],
    "zimage_text_encoder": ["z-image/Tongyi-MAI/Z-Image/text_encoder/model-00001-of-00003.safetensors"],
    "zimage_base_weights": [],

    # Wan2.2 T2V-A14B
    "wan_vae": ["wan/Wan2.2-T2V-A14B/Wan2.1_VAE.pth"],
    "wan_t5": ["wan/Wan2.2-T2V-A14B/models_t5_umt5-xxl-enc-bf16.pth"],
    "wan_dit": [
        "wan/Wan2.2-T2V-A14B/low_noise_model/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.2-T2V-A14B/low_noise_model",
    ],
    "wan_dit_high_noise": [
        "wan/Wan2.2-T2V-A14B/high_noise_model/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.2-T2V-A14B/high_noise_model",
    ],

    # Wan2.2 I2V-A14B
    "wan22_i2v_vae": ["wan/Wan2.2-I2V-A14B/Wan2.1_VAE.pth"],
    "wan22_i2v_t5": ["wan/Wan2.2-I2V-A14B/models_t5_umt5-xxl-enc-bf16.pth"],
    "wan22_i2v_dit": [
        "wan/Wan2.2-I2V-A14B/low_noise_model/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.2-I2V-A14B/low_noise_model",
    ],
    "wan22_i2v_dit_high_noise": [
        "wan/Wan2.2-I2V-A14B/high_noise_model/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.2-I2V-A14B/high_noise_model",
    ],

    # Wan2.2 TI2V-5B
    "wan22_ti2v_vae": [
        "wan/Wan2.2-TI2V-5B/Wan2.2_VAE.pth",
        "wan/Wan2.2-TI2V-5B/Wan2.1_VAE.pth",
    ],
    "wan22_ti2v_t5": ["wan/Wan2.2-TI2V-5B/models_t5_umt5-xxl-enc-bf16.pth"],
    "wan22_ti2v_dit": [
        "wan/Wan2.2-TI2V-5B/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.2-TI2V-5B",
    ],

    # Wan2.1 T2V-14B. These are also useful starting defaults for the generic Wan2.1 profile.
    "wan21_vae": ["wan/Wan2.1-T2V-14B/Wan2.1_VAE.pth"],
    "wan21_t5": ["wan/Wan2.1-T2V-14B/models_t5_umt5-xxl-enc-bf16.pth"],
    "wan21_dit": [
        "wan/Wan2.1-T2V-14B/diffusion_pytorch_model.safetensors.index.json",
        "wan/Wan2.1-T2V-14B",
    ],

    # Wan single-frame: no dedicated download target yet, so leave empty unless user points to a model manually.
    "wan_sf_vae": [],
    "wan_sf_t5": [],
    "wan_sf_dit": [],

    # HunyuanVideo
    "hv_vae": [
        "hunyuan-video/HunyuanVideo/hunyuan-video-t2v-720p/vae/pytorch_model.pt",
        "hunyuan-video/HunyuanVideo/vae/pytorch_model.pt",
    ],
    "hv_text_encoder": [
        "hunyuan-video/HunyuanVideo/text_encoder/pytorch_model.bin",
        "hunyuan-video/HunyuanVideo/text_encoder",
    ],
    "hv_dit": [
        "hunyuan-video/HunyuanVideo/hunyuan-video-t2v-720p/transformers/mp_rank_00_model_states.pt",
        "hunyuan-video/HunyuanVideo/transformers/mp_rank_00_model_states.pt",
        "hunyuan-video/HunyuanVideo",
    ],

    # Qwen-Image
    "qwen_image_vae": ["qwen/Qwen-Image/vae/diffusion_pytorch_model.safetensors"],
    "qwen_image_text_encoder": [
        "qwen/Qwen-Image/text_encoder/model.safetensors",
        "qwen/Qwen-Image/text_encoder",
    ],
    "qwen_image_dit": [
        "qwen/Qwen-Image/transformer/diffusion_pytorch_model.safetensors.index.json",
        "qwen/Qwen-Image/transformer",
    ],

    # FLUX.1 Kontext
    "flux_kontext_vae": ["flux/FLUX.1-Kontext-dev/vae/diffusion_pytorch_model.safetensors"],
    "flux_kontext_clip_l": [
        "flux/FLUX.1-Kontext-dev/text_encoder/model.safetensors",
        "flux/FLUX.1-Kontext-dev/text_encoder",
    ],
    "flux_kontext_t5": [
        "flux/FLUX.1-Kontext-dev/text_encoder_2/model.safetensors",
        "flux/FLUX.1-Kontext-dev/text_encoder_2",
    ],
    "flux_kontext_dit": [
        "flux/FLUX.1-Kontext-dev/transformer/diffusion_pytorch_model.safetensors.index.json",
        "flux/FLUX.1-Kontext-dev/transformer",
    ],

    # FLUX.2 dev
    "flux2_dev_vae": ["flux/FLUX.2-dev/vae/diffusion_pytorch_model.safetensors"],
    "flux2_dev_text_encoder": [
        "flux/FLUX.2-dev/text_encoder_2/model.safetensors",
        "flux/FLUX.2-dev/text_encoder_2",
        "flux/FLUX.2-dev/text_encoder/model.safetensors",
        "flux/FLUX.2-dev/text_encoder",
    ],
    "flux2_dev_dit": [
        "flux/FLUX.2-dev/transformer/diffusion_pytorch_model.safetensors.index.json",
        "flux/FLUX.2-dev/transformer",
    ],

    # FLUX.2 klein
    "flux2_klein_vae": ["flux/FLUX.2-klein/vae/diffusion_pytorch_model.safetensors"],
    "flux2_klein_text_encoder": [
        "flux/FLUX.2-klein/text_encoder_2/model.safetensors",
        "flux/FLUX.2-klein/text_encoder_2",
        "flux/FLUX.2-klein/text_encoder/model.safetensors",
        "flux/FLUX.2-klein/text_encoder",
    ],
    "flux2_klein_dit": [
        "flux/FLUX.2-klein/transformer/diffusion_pytorch_model.safetensors.index.json",
        "flux/FLUX.2-klein/transformer",
    ],

    # These are placeholders until their official download layouts are verified.
    "hv15_vae": [],
    "hv15_text_encoder": [],
    "hv15_dit": [],
    "fpack_vae": [],
    "fpack_text_encoder": [],
    "fpack_dit": [],
    "fpack_sf_vae": [],
    "fpack_sf_text_encoder": [],
    "fpack_sf_dit": [],
    "hidream_o1_vae": [],
    "hidream_o1_text_encoder": [],
    "hidream_o1_dit": [],
    "kandinsky5_vae": [],
    "kandinsky5_text_encoder": [],
    "kandinsky5_dit": [],
    "ideogram4_vae": [],
    "ideogram4_text_encoder": [],
    "ideogram4_dit": [],
    "krea2_vae": [],
    "krea2_text_encoder": [],
    "krea2_dit": [],
}


def repo_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def setting_value_for(path: Path) -> str:
    try:
        return "../" + path.relative_to(ROOT.parent).as_posix()
    except ValueError:
        return path.as_posix()


def first_existing(models_dir: Path, candidates: list[str]) -> Path | None:
    for rel in candidates:
        candidate = models_dir / rel
        if candidate.exists():
            return candidate
    return None


def load_settings(path: Path) -> dict:
    if path.exists():
        return toml.load(path)
    if DEFAULT_EXAMPLE.exists():
        return toml.load(DEFAULT_EXAMPLE)
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply downloaded model paths to configs/settings.toml")
    parser.add_argument("--models-dir", default=str(DEFAULT_MODELS_DIR), help="download root, default: ~/models")
    parser.add_argument("--settings", default=str(DEFAULT_SETTINGS), help="settings.toml path")
    parser.add_argument("--dry-run", action="store_true", help="show changes without writing")
    parser.add_argument("--keep-existing", action="store_true", help="do not overwrite non-empty existing values")
    args = parser.parse_args()

    models_dir = Path(args.models_dir).expanduser().resolve()
    settings_path = Path(args.settings).expanduser().resolve()
    data = load_settings(settings_path)
    data.setdefault("model_paths", {})
    model_paths = data["model_paths"]

    print(f"Models dir:   {models_dir}")
    print(f"Settings file: {settings_path}")
    print("")

    updated = 0
    missing = 0
    kept = 0

    for key, candidates in MODEL_PATH_CANDIDATES.items():
        old_value = str(model_paths.get(key, "") or "")
        if args.keep_existing and old_value:
            print(f"KEEP  {key}: {old_value}")
            kept += 1
            continue
        found = first_existing(models_dir, candidates)
        if found is None:
            model_paths.setdefault(key, old_value)
            print(f"MISS  {key}")
            missing += 1
            continue
        new_value = setting_value_for(found)
        model_paths[key] = new_value
        if new_value != old_value:
            print(f"SET   {key}: {new_value}")
            updated += 1
        else:
            print(f"OK    {key}: {new_value}")

    print("")
    print(f"Summary: updated={updated}, kept={kept}, missing={missing}")

    if args.dry_run:
        print("Dry run: settings.toml was not changed.")
        return 0

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(toml.dumps(data), encoding="utf-8")
    print(f"Wrote: {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
