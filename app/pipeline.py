from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import toml
from PIL import Image

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

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        if not path.exists():
            example = path.with_name("settings.example.toml")
            raise FileNotFoundError(f"settings.toml がありません。まず {example} をコピーしてください。")
        data = toml.load(path)
        return cls(
            musubi_repo_path=Path(data["musubi"]["repo_path"]),
            musubi_python_path=Path(data["musubi"]["python_path"]),
            datasets_dir=Path(data["paths"]["datasets_dir"]),
            outputs_dir=Path(data["paths"]["outputs_dir"]),
            comfyui_loras_dir=Path(data["paths"]["comfyui_loras_dir"]),
            llm_endpoint=data["caption"].get("llm_endpoint", ""),
            llm_model=data["caption"].get("llm_model", ""),
        )


def image_files(dataset_dir: Path) -> list[Path]:
    return sorted(p for p in dataset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)


def check_dataset(dataset_dir: Path) -> str:
    if not dataset_dir.exists():
        return f"NG: フォルダが存在しません: {dataset_dir}"
    imgs = image_files(dataset_dir)
    if not imgs:
        return "NG: 画像が見つかりません。"

    problems: list[str] = []
    size_counts: dict[str, int] = {}
    caption_missing = 0
    for img_path in imgs:
        try:
            with Image.open(img_path) as im:
                size_counts[f"{im.width}x{im.height}"] = size_counts.get(f"{im.width}x{im.height}", 0) + 1
                if min(im.width, im.height) < 512:
                    problems.append(f"小さめ: {img_path.name} {im.width}x{im.height}")
        except Exception as exc:
            problems.append(f"読込失敗: {img_path.name}: {exc}")
        if not img_path.with_suffix(".txt").exists():
            caption_missing += 1

    lines = [
        f"画像数: {len(imgs)}",
        f"caption未作成: {caption_missing}",
        "サイズ内訳:",
    ]
    lines += [f"- {k}: {v}" for k, v in sorted(size_counts.items())]
    if problems:
        lines.append("\n注意:")
        lines += [f"- {p}" for p in problems[:30]]
        if len(problems) > 30:
            lines.append(f"...他 {len(problems)-30} 件")
    return "\n".join(lines)


def prompt_for_lora_type(lora_type: str) -> str:
    prompts = {
        "eye": "Describe only the eyes: iris color, eyelids, eyelashes, eye shape, gaze, makeup. Do not mention hair, face, clothes, background, age, or gender.",
        "mouth": "Describe only the mouth and lips: lip shape, expression, teeth visibility, smile, lipstick. Do not mention eyes, hair, clothes, background, age, or gender.",
        "face": "Describe only face identity features and expression. Avoid clothes and background.",
        "hair": "Describe only hair: length, style, texture, color, bangs. Avoid face, clothes, and background.",
        "hand": "Describe only hands: pose, fingers, nails, gesture. Avoid face, clothes, and background.",
        "style": "Describe visual style, lighting, rendering, color palette, and artistic features.",
        "clothing": "Describe only clothing: garment type, fabric, pattern, color, accessories. Avoid face and background.",
    }
    return prompts.get(lora_type, prompts["style"])


def generate_captions_placeholder(dataset_dir: Path, lora_type: str, caption_mode: str, cfg: AppConfig) -> str:
    """MVP placeholder.

    次の段階で JoyCaption 実行と OpenAI互換LLM API 呼び出しを実装する。
    まずは既存txtが無い画像に、対象別の仮キャプションを書く。
    """
    imgs = image_files(dataset_dir)
    if not imgs:
        return "画像が見つかりません。"
    base = prompt_for_lora_type(lora_type)
    created = 0
    for img in imgs:
        txt = img.with_suffix(".txt")
        if txt.exists():
            continue
        txt.write_text(f"{lora_type} detail, high quality, sharp focus\n", encoding="utf-8")
        created += 1
    return (
        f"caption placeholder作成: {created}件\n"
        f"mode: {caption_mode}\n"
        f"次に実装する指示:\n{base}\n"
        "JoyCaption → LLM整形は次フェーズで接続します。"
    )


def build_dataset_toml(dataset_dir: Path, output_dir: Path, resolution: int) -> str:
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
    # 実運用時は target_model ごとに musubi-tuner の cache scripts を呼び分ける。
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
