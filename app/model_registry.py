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


def profile(profile_id: str, display_name: str, task: str, ja: str, en: str) -> ModelProfile:
    return ModelProfile(
        id=profile_id,
        display_name=display_name,
        task=task,
        enabled_in_v1=True,
        description_ja=ja,
        description_en=en,
    )


ALIASES = {
    "wan2.2": "wan2.2-t2v-a14b",
}


PROFILES = {
    "z-image": profile(
        "z-image",
        "Z-Image / Z-Image-Turbo",
        "z-image",
        "Z-Image系DiT用のLoRAを作成します。必要設定はZ-Image DiT、VAE、Text Encoderです。",
        "Create a LoRA for a Z-Image-family DiT. Required settings are Z-Image DiT, VAE, and Text Encoder.",
    ),
    "wan2.2-t2v-a14b": profile(
        "wan2.2-t2v-a14b",
        "Wan2.2 T2V-A14B",
        "t2v-A14B",
        "Wan2.2 Text-to-Video A14B用LoRAを作成します。必要設定はWan VAE、Wan T5、low-noise DiT、high-noise DiTです。",
        "Create a Wan2.2 Text-to-Video A14B LoRA. Required settings are Wan VAE, Wan T5, low-noise DiT, and high-noise DiT.",
    ),
    "wan2.2-i2v-a14b": profile(
        "wan2.2-i2v-a14b",
        "Wan2.2 I2V-A14B",
        "i2v-A14B",
        "Wan2.2 Image-to-Video A14B用LoRAを作成します。I2V用のキャッシュでは画像条件を使うため、Latent cacheにI2V指定を入れます。",
        "Create a Wan2.2 Image-to-Video A14B LoRA. I2V caching uses the image-conditioning option.",
    ),
    "wan2.2-ti2v-5b": profile(
        "wan2.2-ti2v-5b",
        "Wan2.2 TI2V-5B",
        "ti2v-5B",
        "Wan2.2 Text-Image-to-Video 5B用プロファイルです。公式生成はT2V/I2V両対応ですが、Musubi Tunerでの学習コマンドは検証待ちです。",
        "Profile for Wan2.2 Text-Image-to-Video 5B. Official inference supports both T2V and I2V, but the Musubi training command is not verified yet.",
    ),
    "wan2.1": profile(
        "wan2.1",
        "Wan2.1",
        "wan2.1",
        "Wan2.1用LoRAを作成します。Wan2.2とは別プロファイルとして設定を管理します。",
        "Create a Wan2.1 LoRA. Settings are managed separately from Wan2.2.",
    ),
    "wan-single-frame": profile(
        "wan-single-frame",
        "Wan2.1/2.2 Single Frame",
        "wan-single-frame",
        "Wan2.1/2.2のSingle Frame学習用プロファイルです。",
        "Profile for Wan2.1/2.2 Single Frame LoRA training.",
    ),
    "hunyuan-video": profile(
        "hunyuan-video",
        "HunyuanVideo",
        "hunyuan-video",
        "HunyuanVideo用LoRAを作成するためのプロファイルです。",
        "Profile for HunyuanVideo LoRA training.",
    ),
    "hunyuan-video-1.5": profile(
        "hunyuan-video-1.5",
        "HunyuanVideo 1.5",
        "hunyuan-video-1.5",
        "HunyuanVideo 1.5用LoRAを作成するためのプロファイルです。",
        "Profile for HunyuanVideo 1.5 LoRA training.",
    ),
    "framepack": profile(
        "framepack",
        "FramePack",
        "framepack",
        "FramePack用LoRAを作成するためのプロファイルです。",
        "Profile for FramePack LoRA training.",
    ),
    "framepack-single-frame": profile(
        "framepack-single-frame",
        "FramePack Single Frame",
        "framepack-single-frame",
        "FramePack Single Frame学習用プロファイルです。",
        "Profile for FramePack Single Frame LoRA training.",
    ),
    "flux-kontext": profile(
        "flux-kontext",
        "FLUX.1 Kontext",
        "flux-kontext",
        "FLUX.1 Kontext用LoRAを作成するためのプロファイルです。",
        "Profile for FLUX.1 Kontext LoRA training.",
    ),
    "flux2-dev": profile(
        "flux2-dev",
        "FLUX.2 dev",
        "flux2-dev",
        "FLUX.2 dev用LoRAを作成するためのプロファイルです。",
        "Profile for FLUX.2 dev LoRA training.",
    ),
    "flux2-klein": profile(
        "flux2-klein",
        "FLUX.2 klein",
        "flux2-klein",
        "FLUX.2 klein用LoRAを作成するためのプロファイルです。",
        "Profile for FLUX.2 klein LoRA training.",
    ),
    "qwen-image": profile(
        "qwen-image",
        "Qwen-Image",
        "qwen-image",
        "Qwen-Image用LoRAを作成するためのプロファイルです。",
        "Profile for Qwen-Image LoRA training.",
    ),
    "hidream-o1": profile(
        "hidream-o1",
        "HiDream-O1-Image",
        "hidream-o1",
        "HiDream-O1-Image用LoRAを作成するためのプロファイルです。",
        "Profile for HiDream-O1-Image LoRA training.",
    ),
    "kandinsky5": profile(
        "kandinsky5",
        "Kandinsky 5",
        "kandinsky5",
        "Kandinsky 5用LoRAを作成するためのプロファイルです。",
        "Profile for Kandinsky 5 LoRA training.",
    ),
    "ideogram4": profile(
        "ideogram4",
        "Ideogram4",
        "ideogram4",
        "Ideogram4用LoRAを作成するためのプロファイルです。",
        "Profile for Ideogram4 LoRA training.",
    ),
    "krea2": profile(
        "krea2",
        "Krea 2",
        "krea2",
        "Krea 2用LoRAを作成するためのプロファイルです。",
        "Profile for Krea 2 LoRA training.",
    ),
}


def normalize_profile_id(profile_id: str) -> str:
    return ALIASES.get(profile_id, profile_id)


def get_profile(profile_id: str) -> ModelProfile:
    return PROFILES.get(normalize_profile_id(profile_id), PROFILES["z-image"])


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
