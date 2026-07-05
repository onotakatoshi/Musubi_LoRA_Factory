from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS_DIR = ROOT.parent / "models"


@dataclass(frozen=True)
class FileSpec:
    key: str
    names: tuple[str, ...]
    must_contain: tuple[str, ...] = ()
    prefer_contain: tuple[str, ...] = ()
    avoid_contain: tuple[str, ...] = ()


KNOWN_FILES: tuple[FileSpec, ...] = (
    FileSpec("zimage_vae", ("diffusion_pytorch_model.safetensors",), ("Z-Image", "vae")),
    FileSpec("zimage_text_encoder", ("model-00001-of-00003.safetensors",), ("Z-Image", "text_encoder")),
    FileSpec("zimage_dit", ("diffusion_pytorch_model.safetensors.index.json", "diffusion_pytorch_model-00001-of-00002.safetensors"), ("Z-Image", "transformer")),

    FileSpec("wan_vae", ("Wan2.1_VAE.pth",), ("Wan2.2-T2V-A14B",)),
    FileSpec("wan_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-T2V-A14B",)),
    FileSpec("wan_dit", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.2-T2V-A14B", "low_noise_model")),
    FileSpec("wan_dit_high_noise", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.2-T2V-A14B", "high_noise_model")),

    FileSpec("wan22_i2v_vae", ("Wan2.1_VAE.pth",), ("Wan2.2-I2V-A14B",)),
    FileSpec("wan22_i2v_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-I2V-A14B",)),
    FileSpec("wan22_i2v_dit", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.2-I2V-A14B", "low_noise_model")),
    FileSpec("wan22_i2v_dit_high_noise", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.2-I2V-A14B", "high_noise_model")),

    FileSpec("wan22_ti2v_vae", ("Wan2.2_VAE.pth", "Wan2.1_VAE.pth"), ("Wan2.2-TI2V-5B",)),
    FileSpec("wan22_ti2v_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.2-TI2V-5B",)),
    FileSpec("wan22_ti2v_dit", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.2-TI2V-5B",)),

    FileSpec("wan21_vae", ("Wan2.1_VAE.pth",), ("Wan2.1-T2V-14B",)),
    FileSpec("wan21_t5", ("models_t5_umt5-xxl-enc-bf16.pth",), ("Wan2.1-T2V-14B",)),
    FileSpec("wan21_dit", ("diffusion_pytorch_model.safetensors.index.json",), ("Wan2.1-T2V-14B",)),

    FileSpec("qwen_image_vae", ("diffusion_pytorch_model.safetensors",), ("Qwen-Image", "vae")),
    FileSpec("qwen_image_text_encoder", ("model.safetensors",), ("Qwen-Image", "text_encoder")),
    FileSpec("qwen_image_dit", ("diffusion_pytorch_model.safetensors.index.json", "diffusion_pytorch_model.safetensors"), ("Qwen-Image", "transformer")),

    FileSpec("flux_kontext_vae", ("diffusion_pytorch_model.safetensors",), ("FLUX.1-Kontext", "vae")),
    FileSpec("flux_kontext_clip_l", ("model.safetensors",), ("FLUX.1-Kontext", "text_encoder")),
    FileSpec("flux_kontext_t5", ("model.safetensors",), ("FLUX.1-Kontext", "text_encoder_2")),
    FileSpec("flux_kontext_dit", ("diffusion_pytorch_model.safetensors.index.json", "diffusion_pytorch_model.safetensors"), ("FLUX.1-Kontext", "transformer")),

    FileSpec("flux2_dev_vae", ("diffusion_pytorch_model.safetensors",), ("FLUX.2-dev", "vae")),
    FileSpec("flux2_dev_text_encoder", ("model.safetensors",), ("FLUX.2-dev", "text_encoder"), ("text_encoder_2",)),
    FileSpec("flux2_dev_dit", ("diffusion_pytorch_model.safetensors.index.json", "diffusion_pytorch_model.safetensors"), ("FLUX.2-dev", "transformer")),

    FileSpec("flux2_klein_vae", ("diffusion_pytorch_model.safetensors",), ("FLUX.2-klein", "vae")),
    FileSpec("flux2_klein_text_encoder", ("model.safetensors",), ("FLUX.2-klein", "text_encoder"), ("text_encoder_2",)),
    FileSpec("flux2_klein_dit", ("diffusion_pytorch_model.safetensors.index.json", "diffusion_pytorch_model.safetensors"), ("FLUX.2-klein", "transformer")),

    FileSpec("hv_vae", ("pytorch_model.pt", "diffusion_pytorch_model.safetensors"), ("HunyuanVideo", "vae")),
    FileSpec("hv_text_encoder", ("pytorch_model.bin", "model.safetensors"), ("HunyuanVideo", "text_encoder")),
    FileSpec("hv_dit", ("mp_rank_00_model_states.pt", "diffusion_pytorch_model.safetensors", "diffusion_pytorch_model.safetensors.index.json"), ("HunyuanVideo",), ("transformer", "transformers"), ("vae", "text_encoder")),
)


def setting_value(path: Path) -> str:
    try:
        return "../" + path.resolve().relative_to(ROOT.parent.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _score(path: Path, spec: FileSpec) -> tuple[int, str]:
    text = path.as_posix().lower()
    score = 0
    for token in spec.prefer_contain:
        if token.lower() in text:
            score += 10
    for token in spec.avoid_contain:
        if token.lower() in text:
            score -= 20
    return (-score, text)


def _find_one(models_dir: Path, spec: FileSpec) -> Path | None:
    if not models_dir.exists():
        return None
    matches: list[Path] = []
    wanted_names = {name.lower() for name in spec.names}
    required = tuple(token.lower() for token in spec.must_contain)
    for path in models_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name.lower() not in wanted_names:
            continue
        text = path.as_posix().lower()
        if all(token.lower() in text for token in required):
            matches.append(path)
    if not matches:
        return None
    return sorted(matches, key=lambda p: _score(p, spec))[0]


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
