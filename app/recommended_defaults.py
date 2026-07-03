from __future__ import annotations

DEFAULTS = {
    "resolution": 512,
    "rank": 16,
    "alpha": 16,
    "epochs": 10,
    "lr": 0.00005,
}


def status_text(name: str, value: int | float, lang: str = "日本語") -> str:
    default = DEFAULTS[name]
    is_default = value == default
    if lang == "English":
        return "Recommended default" if is_default else f"Custom value / default: {default}"
    return "推奨デフォルト" if is_default else f"ユーザー設定 / デフォルト: {default}"


def help_text(name: str, lang: str = "日本語") -> str:
    ja = {
        "resolution": "推奨デフォルト: 512。最初は512が安全です。768/1024は品質向上の可能性がありますが、メモリ使用量と学習時間が増えます。",
        "rank": "推奨デフォルト: 16。LoRAの表現力です。大きいほど覚えますが、重くなり過学習もしやすくなります。",
        "alpha": "推奨デフォルト: 16。通常はRankと同じ値から始めます。LoRAの効き方に関係します。",
        "epochs": "推奨デフォルト: 10。データセットを何周学習するかです。効きが弱ければ増やし、強すぎれば減らします。",
        "lr": "推奨デフォルト: 0.00005。学習率です。最初は変更しないことを推奨します。大きすぎると破綻しやすくなります。",
    }
    en = {
        "resolution": "Recommended default: 512. Start with 512. 768/1024 may improve quality but uses more memory and time.",
        "rank": "Recommended default: 16. Higher rank increases capacity but can be heavier and overfit more easily.",
        "alpha": "Recommended default: 16. Usually start with the same value as Rank.",
        "epochs": "Recommended default: 10. Increase if too weak, decrease if overtrained.",
        "lr": "Recommended default: 0.00005. Keep this unchanged at first. Too high can break training.",
    }
    return (en if lang == "English" else ja)[name]
