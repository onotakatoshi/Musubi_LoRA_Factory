from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingPreset:
    name: str
    lora_type: str
    rank: int
    alpha: int
    epochs: int
    lr: float
    resolution: int
    note_ja: str
    note_en: str


PRESETS = {
    "eye": TrainingPreset("eye", "eye", 16, 16, 10, 0.00005, 512, "目LoRAの初回向け。過学習しにくい控えめ設定です。", "Good first preset for eye LoRA."),
    "mouth": TrainingPreset("mouth", "mouth", 16, 16, 10, 0.00005, 512, "口・唇LoRAの初回向け。まずはこの設定で確認します。", "Good first preset for mouth/lips LoRA."),
    "hair": TrainingPreset("hair", "hair", 16, 16, 12, 0.00005, 512, "髪LoRA向け。形状差が出やすいので少しだけEpochを増やします。", "Hair LoRA preset with slightly more epochs."),
    "hand": TrainingPreset("hand", "hand", 16, 16, 12, 0.00004, 512, "手LoRA向け。崩れやすいので学習率を少し控えめにします。", "Hand LoRA preset with slightly lower LR."),
    "style": TrainingPreset("style", "style", 32, 32, 10, 0.00005, 768, "スタイルLoRA向け。部分LoRAより広く覚えるためRankと解像度を上げます。", "Style LoRA preset with higher rank/resolution."),
    "clothing": TrainingPreset("clothing", "clothing", 16, 16, 12, 0.00005, 512, "服LoRA向け。最初は512で安定確認します。", "Clothing LoRA preset for stable first runs."),
}


def preset_names() -> list[str]:
    return list(PRESETS.keys())


def get_preset(name: str) -> TrainingPreset:
    return PRESETS.get(name, PRESETS["eye"])


def preset_summary(name: str, lang: str = "日本語") -> str:
    p = get_preset(name)
    note = p.note_en if lang == "English" else p.note_ja
    if lang == "English":
        return f"{p.name}: Rank={p.rank}, Alpha={p.alpha}, Epochs={p.epochs}, LR={p.lr}, Resolution={p.resolution}\n{note}"
    return f"{p.name}: Rank={p.rank}, Alpha={p.alpha}, Epochs={p.epochs}, LR={p.lr}, Resolution={p.resolution}\n{note}"
