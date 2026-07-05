from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    id: str
    display_name: str
    task: str
    enabled_in_v1: bool
    description_ja: str
    description_en: str


PROFILES = {
    "z-image": ModelProfile(
        id="z-image",
        display_name="Z-Image / Z-Image-Turbo",
        task="z-image",
        enabled_in_v1=True,
        description_ja="Z-Image系DiT用のLoRAを作成します。必要設定はZ-Image DiT、VAE、Text Encoderです。生成時はZ-Image / Z-Image-Turbo系ワークフローでLoRAを使います。",
        description_en="Create a LoRA for a Z-Image-family DiT. Required settings are Z-Image DiT, VAE, and Text Encoder. Use the LoRA in a Z-Image / Z-Image-Turbo workflow.",
    ),
    "wan2.2": ModelProfile(
        id="wan2.2",
        display_name="Wan2.2",
        task="t2v-A14B",
        enabled_in_v1=True,
        description_ja="Wan2.2用LoRAを作成します。必要設定はWan VAE、Wan T5、Wan2.2 low-noise DiTです。high-noise DiTを指定すると2系統DiTでコマンドを作ります。",
        description_en="Create a Wan2.2 LoRA. Required settings are Wan VAE, Wan T5, and Wan2.2 low-noise DiT. If high-noise DiT is set, commands use the dual-DiT setup.",
    ),
}


def get_profile(profile_id: str) -> ModelProfile:
    return PROFILES.get(profile_id, PROFILES["z-image"])


def enabled_profiles(include_future: bool = False) -> list[ModelProfile]:
    values = list(PROFILES.values())
    if include_future:
        return values
    return [p for p in values if p.enabled_in_v1]


def default_profile() -> ModelProfile:
    return PROFILES["z-image"]


def profile_ids(include_future: bool = False) -> list[str]:
    return [p.id for p in enabled_profiles(include_future=include_future)]


def profile_summary(profile_id: str, lang: str = "日本語") -> str:
    p = get_profile(profile_id)
    description = p.description_en if lang == "English" else p.description_ja
    status = "Enabled" if p.enabled_in_v1 else "Future"
    if lang == "日本語":
        status = "対応" if p.enabled_in_v1 else "将来対応"
    return f"{p.display_name}\nProfile ID: {p.id}\nTask: {p.task}\nStatus: {status}\n{description}"
