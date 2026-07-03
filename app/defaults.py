from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DefaultValue:
    key: str
    value: int | float
    unit: str
    reason_ja: str
    reason_en: str


DEFAULTS = {
    "resolution": DefaultValue("resolution", 512, "px", "推奨デフォルト。最初の学習は512が安定です。", "Recommended default. 512 is stable for first runs."),
    "rank": DefaultValue("rank", 16, "", "推奨デフォルト。体の一部LoRAではまず16が扱いやすいです。", "Recommended default. Rank 16 is a good first choice for body-part LoRA."),
    "alpha": DefaultValue("alpha", 16, "", "Rankと同じ値。最初はRank=Alphaが分かりやすいです。", "Same as Rank. Rank=Alpha is easiest to understand at first."),
    "epochs": DefaultValue("epochs", 10, "", "推奨デフォルト。100枚前後の画像で最初に試す値です。", "Recommended default for an initial run with around 100 images."),
    "learning_rate": DefaultValue("learning_rate", 0.00005, "", "推奨デフォルト。大きすぎると壊れやすく、小さすぎると覚えにくいです。", "Recommended default. Too high can break training; too low may underfit."),
}


def default_value(key: str) -> int | float:
    return DEFAULTS[key].value


def is_default(key: str, value: int | float) -> bool:
    default = DEFAULTS[key].value
    if isinstance(default, float):
        return abs(float(value) - default) < 1e-12
    return int(value) == int(default)


def status_text(key: str, value: int | float, lang: str) -> str:
    d = DEFAULTS[key]
    label_default = "推奨デフォルト" if lang == "日本語" else "Recommended default"
    label_custom = "ユーザー設定" if lang == "日本語" else "Custom value"
    reason = d.reason_ja if lang == "日本語" else d.reason_en
    shown = f"{d.value}{d.unit}" if d.unit else str(d.value)
    if is_default(key, value):
        return f"🟢 {label_default}: {shown}\n{reason}"
    return f"🟡 {label_custom}\nDefault: {shown}\n{reason}"
