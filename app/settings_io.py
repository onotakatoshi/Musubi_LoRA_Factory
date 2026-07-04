from __future__ import annotations

from pathlib import Path
from typing import Any

import toml


ZIMAGE_MODEL_ROOT = "../models/z-image/Tongyi-MAI/Z-Image"


def default_settings() -> dict[str, Any]:
    return {
        "ui": {
            "language": "日本語",
        },
        "musubi": {
            "repo_path": "../musubi-tuner",
            "python_path": "../musubi-tuner/.venv/bin/python",
        },
        "paths": {
            "datasets_dir": "datasets/lora",
            "outputs_dir": "outputs/lora",
            "comfyui_loras_dir": "../ComfyUI/models/loras",
        },
        "caption": {
            "mode": "manual",
            "joycaption_command": "",
            "llm_endpoint": "",
            "llm_model": "",
        },
        "model_paths": {
            "zimage_dit": f"{ZIMAGE_MODEL_ROOT}/transformer/diffusion_pytorch_model-00001-of-00002.safetensors",
            "zimage_vae": f"{ZIMAGE_MODEL_ROOT}/vae/diffusion_pytorch_model.safetensors",
            "zimage_text_encoder": f"{ZIMAGE_MODEL_ROOT}/text_encoder/model-00001-of-00003.safetensors",
            "zimage_base_weights": "",
            "wan_vae": "../models/wan/Wan2.1_VAE.pth",
            "wan_t5": "../models/wan/models_t5_umt5-xxl-enc-bf16.pth",
            "wan_dit": "../models/wan/wan2.2_low_noise.safetensors",
            "wan_dit_high_noise": "../models/wan/wan2.2_high_noise.safetensors",
        },
    }


def load_settings(path: Path) -> dict[str, Any]:
    data = default_settings()
    if path.exists():
        loaded = toml.load(path)
        for section, values in loaded.items():
            if isinstance(values, dict) and section in data:
                data[section].update(values)
            else:
                data[section] = values
    return data


def save_settings(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(toml.dumps(data), encoding="utf-8")


def nested_get(data: dict[str, Any], section: str, key: str, default: str = "") -> str:
    value = data.get(section, {}).get(key, default)
    return str(value) if value is not None else ""
