from __future__ import annotations

from model_registry import normalize_profile_id

# Shared fallback for profiles without their own entry.
DEFAULTS = {
    "resolution": 512,
    "rank": 16,
    "alpha": 16,
    "epochs": 16,
    "lr": 0.00005,
}

# Per-profile recommendations. Every rank/alpha/lr below is the value used by the LoRA
# training example in that model's musubi-tuner doc, so these track upstream instead of
# being invented here. The full fine-tune examples in the same docs use much lower
# learning rates (1e-6) and are deliberately not used.
#
#   z-image        docs/zimage.md          network_dim 32,  learning_rate 1e-4
#   wan            docs/wan.md             network_dim 32,  learning_rate 2e-4
#   hunyuan video  docs/hunyuan_video.md   network_dim 32,  learning_rate 2e-4
#   flux kontext   docs/flux_kontext.md    network_dim 32,  learning_rate 1e-4
#   flux 2         docs/flux_2.md          network_dim 32,  learning_rate 1e-4
#   qwen image     docs/qwen_image.md      network_dim 16,  learning_rate 5e-5
#   minimax h3     docs/minimax_h3.md      network_dim 16,  network_alpha 16, learning_rate 1e-4
#
# Every one of those docs uses --max_train_epochs 16, which is why the shared default is
# 16 and no profile overrides it. Resolution is not prescribed by the docs (it lives in
# the dataset TOML); MiniMax-H3 is set to 1024 because that is the value verified on a
# real one-frame run here, and H3 requires multiples of 32.
PROFILE_DEFAULTS: dict[str, dict[str, int | float]] = {
    "z-image": {"rank": 32, "alpha": 32, "lr": 1e-4},
    "wan2.2-t2v-a14b": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "wan2.2-i2v-a14b": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "wan2.2-ti2v-5b": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "wan2.1": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "wan-single-frame": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "hunyuan-video": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "hunyuan-video-1.5": {"rank": 32, "alpha": 32, "lr": 2e-4},
    "flux-kontext": {"rank": 32, "alpha": 32, "lr": 1e-4},
    "flux2-dev": {"rank": 32, "alpha": 32, "lr": 1e-4},
    "flux2-klein": {"rank": 32, "alpha": 32, "lr": 1e-4},
    "qwen-image": {"rank": 16, "alpha": 16, "lr": 5e-5},
    "minimax-h3": {"rank": 16, "alpha": 16, "lr": 1e-4, "resolution": 1024},
}


def defaults_for(profile_id: str = "") -> dict[str, int | float]:
    """Recommended values for a profile, falling back to the shared defaults."""
    merged = dict(DEFAULTS)
    merged.update(PROFILE_DEFAULTS.get(normalize_profile_id(profile_id or ""), {}))
    return merged


def default_value(name: str, profile_id: str = "") -> int | float:
    return defaults_for(profile_id)[name]


def format_default(name: str, profile_id: str = "") -> str:
    value = default_value(name, profile_id)
    return f"{float(value):.5f}" if name == "lr" else str(value)


REASONS_JA = {
    "resolution": "最初の学習は512が安定です。MiniMax-H3は32の倍数が必要で、1024で検証済みです。",
    "rank": "LoRAの表現力です。モデルごとにmusubi-tunerの例に合わせています。",
    "alpha": "Rankと同じ値です。",
    "epochs": "musubi-tunerの各モデルの例がいずれも16です。必要量は 枚数×epochs のステップ数で決まります。",
    "lr": "大きすぎると壊れやすく、小さすぎると覚えにくくなります。モデルごとにmusubi-tunerの例に合わせています。",
}

REASONS_EN = {
    "resolution": "512 is stable for first runs. MiniMax-H3 needs multiples of 32 and is verified at 1024.",
    "rank": "LoRA capacity. Matched to the musubi-tuner example for each model.",
    "alpha": "Same as Rank.",
    "epochs": "Every musubi-tuner model example uses 16. What matters is total steps: images x epochs.",
    "lr": "Too high can break training; too low may underfit. Matched to the musubi-tuner example for each model.",
}

# Explanation only. The recommended number is prepended at render time so it can never
# disagree with the value the widgets actually use.
HELP_JA = {
    "resolution": "Resolution\n\n学習解像度です。\n768以上は品質が上がりますが重くなります。\nMiniMax-H3は幅・高さとも32の倍数が必要です。",
    "rank": "Rank\n\nLoRAの表現力です。\n大きいほど強く覚えますが、過学習しやすくなりファイルも大きくなります。",
    "alpha": "Alpha\n\nLoRAの効きのスケールです。\n通常はRankと同じ値にします。",
    "epochs": "Epochs\n\nデータセットを何周学習するかです。\n\n重要なのはエポック数ではなく総ステップ数（枚数×epochs）です。20枚なら16でも320ステップ、100枚なら1600ステップになります。枚数が多いときは減らしてください。\n\n毎エポック保存されるので、多めに回して後から良いものを選べます。",
    "lr": "Learning rate\n\n学習率です。\n大きすぎると壊れやすく、小さすぎると覚えにくくなります。",
}

HELP_EN = {
    "resolution": "Resolution\n\nTraining resolution.\n768+ improves quality but costs memory and time.\nMiniMax-H3 needs width and height to be multiples of 32.",
    "rank": "Rank\n\nLoRA capacity.\nHigher learns more strongly but overfits more easily and produces a larger file.",
    "alpha": "Alpha\n\nLoRA strength scale.\nNormally set to the same value as Rank.",
    "epochs": "Epochs\n\nHow many times to iterate over the dataset.\n\nWhat matters is total steps, not epochs: images x epochs. 20 images at 16 epochs is 320 steps; 100 images is 1600. Lower it for larger datasets.\n\nEvery epoch is saved, so running longer and picking the best checkpoint is cheap.",
    "lr": "Learning rate\n\nToo high can break training; too low may underfit.",
}


def help_text(name: str, lang: str = "日本語", profile_id: str = "") -> str:
    body = (HELP_EN if lang == "English" else HELP_JA).get(name, name)
    shown = format_default(name, profile_id)
    header = f"Recommended default: {shown}" if lang == "English" else f"推奨デフォルト: {shown}"
    reason = (REASONS_EN if lang == "English" else REASONS_JA).get(name, "")
    return f"{body}\n\n{header}\n{reason}".strip()


def is_default_value(name: str, value: int | float, profile_id: str = "") -> bool:
    default = default_value(name, profile_id)
    if isinstance(default, float):
        return abs(float(value) - float(default)) < 1e-12
    return int(value) == int(default)


def status_text(name: str, value: int | float, lang: str = "日本語", profile_id: str = "") -> str:
    default = default_value(name, profile_id)
    same = is_default_value(name, value, profile_id)
    reason = (REASONS_EN if lang == "English" else REASONS_JA).get(name, "")
    if lang == "English":
        head = f"🟢 Recommended default: {default}" if same else f"🟡 Custom\nDefault: {default}"
    else:
        head = f"🟢 推奨デフォルト: {default}" if same else f"🟡 ユーザー設定\nデフォルト: {default}"
    return f"{head}\n{reason}".strip()
