from __future__ import annotations

DEFAULTS = {
    "resolution": 512,
    "rank": 16,
    "alpha": 16,
    "epochs": 16,
    "lr": 0.00005,
}

REASONS_JA = {
    "resolution": "最初の学習は512が安定です。",
    "rank": "体の一部LoRAではまず16が扱いやすいです。",
    "alpha": "Rankと同じ値です。まずは Rank=16 / Alpha=16 で始めます。",
    "epochs": "musubi-tunerのMiniMax-H3の例と同じ値です。実際に必要な量は 枚数×epochs のステップ数で決まります。",
    "lr": "大きすぎると壊れやすく、小さすぎると覚えにくくなります。",
}

REASONS_EN = {
    "resolution": "512 is stable for first runs.",
    "rank": "Rank 16 is a good first choice for body-part LoRA.",
    "alpha": "Same as Rank. Start with Rank=16 / Alpha=16.",
    "epochs": "Matches the MiniMax-H3 example in the musubi-tuner docs. What matters is total steps: images x epochs.",
    "lr": "Too high can break training; too low may underfit.",
}

HELP_JA = {
    "resolution": "Resolution\n\n512: 推奨デフォルト。最初の学習は512が安定です。\n768: 品質を上げたい場合。\n1024: 重くなります。まずは非推奨です。",
    "rank": "Rank\n\nLoRAの表現力です。\n16: 推奨デフォルト。体の一部LoRAではまずここから。\n32以上: より強く覚えますが、過学習に注意。",
    "alpha": "Alpha\n\nLoRAの効きのスケールです。\n推奨デフォルトはRankと同じ値です。まずは Rank=16 / Alpha=16 で始めます。",
    "epochs": "Epochs\n\nデータセットを何周学習するかです。\n16: 推奨デフォルト。musubi-tunerのMiniMax-H3の例と同じ値です。\n\n重要なのはエポック数ではなく総ステップ数（枚数×epochs）です。20枚なら16でも320ステップ、100枚なら16で1600ステップになります。枚数が多いときは減らしてください。\n\n毎エポック保存されるので、多めに回して後から良いものを選べます。",
    "lr": "Learning rate\n\n学習率です。\n0.00005: 推奨デフォルト。大きすぎると壊れやすく、小さすぎると覚えにくくなります。",
}

HELP_EN = {
    "resolution": "Resolution\n\n512: Recommended default. Stable for first runs.\n768: Higher quality.\n1024: Heavier; not recommended for the first run.",
    "rank": "Rank\n\nLoRA capacity.\n16: Recommended default for body-part LoRA.\n32+: Stronger learning, but watch for overfitting.",
    "alpha": "Alpha\n\nLoRA strength scale.\nRecommended default is the same as Rank. Start with Rank=16 / Alpha=16.",
    "epochs": "Epochs\n\nHow many times to iterate over the dataset.\n16: Recommended default, matching the MiniMax-H3 example in the musubi-tuner docs.\n\nWhat matters is total steps, not epochs: images x epochs. 20 images at 16 epochs is 320 steps; 100 images at 16 is 1600. Lower it for larger datasets.\n\nEvery epoch is saved, so running longer and picking the best checkpoint is cheap.",
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
