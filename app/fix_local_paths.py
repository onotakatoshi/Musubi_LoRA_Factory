from __future__ import annotations

from pathlib import Path

from settings_io import default_settings, load_settings, save_settings

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"
OLD_HOME_PREFIX = "/home/ono"

PORTABLE_PATHS = {
    "musubi.repo_path": "../musubi-tuner",
    "musubi.python_path": "../musubi-tuner/.venv/bin/python",
    "paths.datasets_dir": "datasets/lora",
    "paths.outputs_dir": "outputs/lora",
    "paths.comfyui_loras_dir": "../ComfyUI/models/loras",
    "model_paths.zimage_dit": "../models/z-image/z_image_base_or_deturbo.safetensors",
    "model_paths.zimage_vae": "../models/z-image/ae.safetensors",
    "model_paths.zimage_text_encoder": "../models/z-image/qwen3_text_encoder_00001-of-00002.safetensors",
    "model_paths.wan_vae": "../models/wan/Wan2.1_VAE.pth",
    "model_paths.wan_t5": "../models/wan/models_t5_umt5-xxl-enc-bf16.pth",
    "model_paths.wan_dit": "../models/wan/wan2.2_low_noise.safetensors",
    "model_paths.wan_dit_high_noise": "../models/wan/wan2.2_high_noise.safetensors",
}


def _portable_value(section: str, key: str, value: str) -> str:
    full_key = f"{section}.{key}"
    if full_key in PORTABLE_PATHS:
        return PORTABLE_PATHS[full_key]
    if value == OLD_HOME_PREFIX:
        return "~"
    if value.startswith(OLD_HOME_PREFIX + "/"):
        return "~/" + value[len(OLD_HOME_PREFIX) + 1:]
    return value


def fix_local_paths(settings_path: Path = SETTINGS_PATH) -> str:
    if not settings_path.exists():
        save_settings(settings_path, default_settings())
        return f"Created settings with portable relative paths: {settings_path}"

    data = load_settings(settings_path)
    changed: list[str] = []
    for section in ["musubi", "paths", "model_paths"]:
        values = data.get(section, {})
        if not isinstance(values, dict):
            continue
        for key, value in list(values.items()):
            if not isinstance(value, str):
                continue
            updated = _portable_value(section, key, value)
            if updated != value:
                values[key] = updated
                changed.append(f"{section}.{key}: {value} -> {updated}")

    save_settings(settings_path, data)
    if not changed:
        return f"Settings already use portable paths: {settings_path}"
    return "Fixed local paths to portable values:\n" + "\n".join(changed)


def main() -> int:
    print(fix_local_paths())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
