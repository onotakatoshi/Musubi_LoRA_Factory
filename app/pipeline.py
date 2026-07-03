from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import toml

from captioning import caption_one_image

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
            raise FileNotFoundError(f"settings.toml がありません。まず {example} をコピーしてください。")
        data = toml.load(path)
        musubi = data.get("musubi", {})
        paths = data.get("paths", {})
        caption = data.get("caption", {})
        return cls(
            musubi_repo_path=Path(musubi.get("repo_path", "/home/ono/musubi-tuner")),
            musubi_python_path=Path(musubi.get("python_path", "python")),
            datasets_dir=Path(paths.get("datasets_dir", "/home/ono/datasets/lora")),
            outputs_dir=Path(paths.get("outputs_dir", "/home/ono/outputs/lora")),
            comfyui_loras_dir=Path(paths.get("comfyui_loras_dir", "/home/ono/ComfyUI/models/loras")),
            llm_endpoint=caption.get("llm_endpoint", ""),
            llm_model=caption.get("llm_model", ""),
            joycaption_command=caption.get("joycaption_command", ""),
        )


def image_files(dataset_dir: Path) -> list[Path]:
    if not dataset_dir.exists():
        return []
    return sorted(p for p in dataset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def check_dataset(dataset_dir: Path, lang: str = "日本語") -> str:
    from dataset_diagnostics import diagnose_dataset

    return diagnose_dataset(dataset_dir, lang=lang)


def generate_captions(dataset_dir: Path, lora_type: str, caption_mode: str, cfg: AppConfig, overwrite: bool = False) -> str:
    imgs = image_files(dataset_dir)
    if not imgs:
        return "画像が見つかりません。"

    created = 0
    skipped = 0
    failed: list[str] = []
    previews: list[str] = []

    for img in imgs:
        txt = img.with_suffix(".txt")
        if txt.exists() and not overwrite:
            skipped += 1
            continue
        try:
            result = caption_one_image(
                img,
                lora_type=lora_type,
                mode=caption_mode,
                joycaption_command=cfg.joycaption_command,
                llm_endpoint=cfg.llm_endpoint,
                llm_model=cfg.llm_model,
            )
            txt.write_text(result.cleaned_caption + "\n", encoding="utf-8")
            created += 1
            if len(previews) < 5:
                previews.append(f"{img.name}: {result.cleaned_caption}")
        except Exception as exc:
            failed.append(f"{img.name}: {exc}")

    lines = [
        f"caption作成: {created}件",
        f"skip: {skipped}件",
        f"mode: {caption_mode}",
    ]
    if previews:
        lines.append("\nPreview:")
        lines += [f"- {p}" for p in previews]
    if failed:
        lines.append("\n失敗:")
        lines += [f"- {f}" for f in failed[:20]]
    return "\n".join(lines)


def generate_captions_placeholder(dataset_dir: Path, lora_type: str, caption_mode: str, cfg: AppConfig) -> str:
    return generate_captions(dataset_dir, lora_type, caption_mode, cfg, overwrite=False)


def build_dataset_toml(dataset_dir: Path, output_dir: Path, resolution: int) -> str:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset folder not found: {dataset_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    toml_path = output_dir / "dataset.toml"
    data = {
        "general": {"resolution": resolution, "caption_extension": ".txt"},
        "datasets": [
            {
                "image_directory": str(dataset_dir),
                "cache_directory": str(cache_dir),
                "num_repeats": 1,
            }
        ],
    }
    toml_path.write_text(toml.dumps(data), encoding="utf-8")
    return str(toml_path)


def run_command(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout


def run_cache_placeholder(dataset_toml: Path, target_model: str, cfg: AppConfig) -> str:
    return (
        "CACHE DRY RUN\n"
        f"target_model: {target_model}\n"
        f"dataset_toml: {dataset_toml}\n"
        f"musubi_repo: {cfg.musubi_repo_path}\n"
        "ここに latent cache / text encoder cache の実コマンドを接続します。"
    )


def run_train_placeholder(
    dataset_toml: Path,
    target_model: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    output_name: str,
    cfg: AppConfig,
) -> str:
    return (
        "TRAIN DRY RUN\n"
        f"target_model: {target_model}\n"
        f"dataset_toml: {dataset_toml}\n"
        f"rank/alpha: {rank}/{alpha}\n"
        f"epochs: {epochs}\n"
        f"learning_rate: {lr}\n"
        f"output_name: {output_name}\n"
        "ここに musubi-tuner の train command を接続します。"
    )


def copy_lora_to_comfyui(lora_path: Path, cfg: AppConfig) -> str:
    if not lora_path.exists():
        return f"NG: LoRAファイルが存在しません: {lora_path}"
    cfg.comfyui_loras_dir.mkdir(parents=True, exist_ok=True)
    dest = cfg.comfyui_loras_dir / lora_path.name
    shutil.copy2(lora_path, dest)
    return f"コピー完了: {dest}"
