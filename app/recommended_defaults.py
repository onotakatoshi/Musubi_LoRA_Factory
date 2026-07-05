from __future__ import annotations

DEFAULTS = {
    "resolution": 512,
    "rank": 16,
    "alpha": 16,
    "epochs": 10,
    "lr": 0.00005,
}

REASONS_JA = {
    "resolution": "最初の学習は512が安定です。",
    "rank": "体の一部LoRAではまず16が扱いやすいです。",
    "alpha": "Rankと同じ値です。まずは Rank=16 / Alpha=16 で始めます。",
    "epochs": "100枚前後の画像で最初に試す値です。",
    "lr": "高すぎると破綻、低すぎると弱くなります。",
}

REASONS_EN = {
    "resolution": "512 is stable for first runs.",
    "rank": "Rank 16 is a good first choice for body-part LoRA.",
    "alpha": "Same as Rank. Start with Rank=16 / Alpha=16.",
    "epochs": "Good initial value for around 100 images.",
    "lr": "Too high can break training; too low may underfit.",
}

HELP_JA = {
    "resolution": "Resolution\n\n512: 推奨デフォルト。最初の学習は512が安定です。\n768: 品質を上げたい場合。\n1024: 重くなります。まずは非推奨です。",
    "rank": "Rank\n\nLoRAの表現力です。\n16: 推奨デフォルト。体の一部LoRAではまずここから。\n32以上: より強く覚えますが、過学習に注意。",
    "alpha": "Alpha\n\nLoRAの効きのスケールです。\n推奨デフォルトはRankと同じ値です。まずは Rank=16 / Alpha=16 で始めます。",
    "epochs": "Epochs\n\nデータセットを何周学習するかです。\n10: 推奨デフォルト。100枚前後の画像で最初に試す値です。",
    "lr": "Learning rate\n\n学習率です。\n0.00005: 推奨デフォルト。大きすぎると壊れやすく、小さすぎると覚えにくくなります。",
}

HELP_EN = {
    "resolution": "Resolution\n\n512: Recommended default. Stable for first runs.\n768: Higher quality.\n1024: Heavier; not recommended for the first run.",
    "rank": "Rank\n\nLoRA capacity.\n16: Recommended default for body-part LoRA.\n32+: Stronger learning, but watch for overfitting.",
    "alpha": "Alpha\n\nLoRA strength scale.\nRecommended default is the same as Rank. Start with Rank=16 / Alpha=16.",
    "epochs": "Epochs\n\nHow many times to iterate over the dataset.\n10: Recommended default for around 100 images.",
    "lr": "Learning rate\n\n0.00005: Recommended default. Too high can break training; too low may underfit.",
}


def help_text(name: str, lang: str = "日本語") -> str:
    return (HELP_EN if lang == "English" else HELP_JA).get(name, name)


def status_text(name: str, value: int | float, lang: str = "日本語") -> str:
    default = DEFAULTS[name]
    same = abs(float(value) - float(default)) < 1e-12 if isinstance(default, float) else int(value) == int(default)
    reason = (REASONS_EN if lang == "English" else REASONS_JA).get(name, "")
    if lang == "English":
        return f"🟢 Recommended default: {default}\n{reason}" if same else f"🟡 Custom value\nDefault: {default}\n{reason}"
    return f"🟢 推奨デフォルト: {default}\n{reason}" if same else f"🟡 ユーザー設定\nデフォルト: {default}\n{reason}"
