from __future__ import annotations

from pathlib import Path

from pipeline import image_files


STEPS = [
    ("1", "Dataset", "画像フォルダを選び、枚数・解像度・caption有無を確認します。"),
    ("2", "Caption", "JoyCaptionとLLMでcaptionを作成します。"),
    ("3", "Review", "captionを一覧で確認し、不要語を削除します。"),
    ("4", "Config", "dataset.tomlを作成します。"),
    ("5", "Train", "cache作成とLoRA学習を実行します。"),
    ("6", "Export", "完成LoRAをComfyUIへコピーします。"),
]


def workflow_markdown(current_step: int = 1) -> str:
    lines = ["## Workflow", ""]
    for number, title, desc in STEPS:
        n = int(number)
        mark = "✅" if n < current_step else "➡️" if n == current_step else "⬜"
        lines.append(f"{mark} **{number}. {title}** — {desc}")
    return "\n".join(lines)


def next_action(dataset_dir: str, dataset_toml: str = "", lora_path: str = "") -> str:
    d = Path(dataset_dir) if dataset_dir else None
    if not d or not d.exists():
        return "次にやること: Datasetフォルダを指定して、`Check Dataset` を押してください。"

    imgs = image_files(d)
    if not imgs:
        return "次にやること: Datasetフォルダに画像を入れてください。まずは512x512の高品質画像100枚が目標です。"

    missing = [p for p in imgs if not p.with_suffix(".txt").exists()]
    if missing:
        return f"次にやること: caption未作成が {len(missing)} 枚あります。`Generate Captions` を押してください。"

    if not dataset_toml:
        return "次にやること: `Caption Editor` でcaptionを確認し、問題なければ `Build dataset.toml` を押してください。"

    if dataset_toml and not Path(dataset_toml).exists():
        return "次にやること: dataset.tomlのパスが見つかりません。`Build dataset.toml` を作り直してください。"

    if not lora_path:
        return "次にやること: `Create Cache` → `Train LoRA` の順に実行してください。"

    if lora_path and not Path(lora_path).exists():
        return "次にやること: LoRAファイルがまだ見つかりません。学習ログを確認してください。"

    return "次にやること: `Copy to ComfyUI` を押して、ComfyUIで生成テストしてください。"
