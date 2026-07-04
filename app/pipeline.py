from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import toml

from path_resolver import resolve_path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass
class AppConfig:
    musubi_repo_path: Path
    musubi_python_path: Path
    datasets_dir: Path
    outputs_dir: Path
    comfyui_loras_dir: Path
    llm_endpoint: str
    llm_model: str
    joycaption_command: str

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        if not path.exists():
            example = path.with_name("settings.example.toml")
            raise FileNotFoundError(f"settings.toml is missing. Copy {example} first.")
        data = toml.load(path)
        musubi = data.get("musubi", {})
        paths = data.get("paths", {})
        caption = data.get("caption", {})
        return cls(
            musubi_repo_path=resolve_path(musubi.get("repo_path", "../musubi-tuner")),
            musubi_python_path=resolve_path(musubi.get("python_path", "../musubi-tuner/.venv/bin/python")),
            datasets_dir=resolve_path(paths.get("datasets_dir", "datasets/lora")),
            outputs_dir=resolve_path(paths.get("outputs_dir", "outputs/lora")),
            comfyui_loras_dir=resolve_path(paths.get("comfyui_loras_dir", "../ComfyUI/models/loras")),
            llm_endpoint=caption.get("llm_endpoint", ""),
            llm_model=caption.get("llm_model", ""),
            joycaption_command=caption.get("joycaption_command", ""),
        )


def image_files(dataset_dir: Path) -> list[Path]:
    resolved = resolve_path(dataset_dir)
    if not resolved.exists():
        return []
    return sorted(p for p in resolved.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def check_dataset(dataset_dir: Path, lang: str = "Japanese") -> str:
    from dataset_diagnostics import diagnose_dataset

    return diagnose_dataset(resolve_path(dataset_dir), lang=lang)


def build_dataset_toml(dataset_dir: Path, output_dir: Path, resolution: int) -> str:
    resolved_dataset_dir = resolve_path(dataset_dir)
    resolved_output_dir = resolve_path(output_dir)
    if not resolved_dataset_dir.exists():
        raise FileNotFoundError(f"Dataset folder not found: {resolved_dataset_dir}")
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = resolved_output_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    toml_path = resolved_output_dir / "dataset.toml"
    data = {
        "general": {"resolution": resolution, "caption_extension": ".txt"},
        "datasets": [{"image_directory": str(resolved_dataset_dir), "cache_directory": str(cache_dir), "num_repeats": 1}],
    }
    toml_path.write_text(toml.dumps(data), encoding="utf-8")
    return str(toml_path)


def copy_lora_to_comfyui(lora_path: Path, cfg: AppConfig) -> str:
    if not lora_path.exists():
        return f"NG: LoRA file does not exist: {lora_path}"
    cfg.comfyui_loras_dir.mkdir(parents=True, exist_ok=True)
    dest = cfg.comfyui_loras_dir / lora_path.name
    shutil.copy2(lora_path, dest)
    return f"Copied: {dest}"
