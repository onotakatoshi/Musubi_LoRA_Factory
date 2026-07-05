from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelField:
    key: str
    label: str
    help_ja: str
    help_en: str
    required: bool = True


@dataclass(frozen=True)
class ModelSettingsSpec:
    profile_id: str
    group_title: str
    fields: tuple[ModelField, ...]
    scripts: tuple[str, ...]
    command_status: str = "catalog_only"


def field(key: str, label: str, help_ja: str, help_en: str, required: bool = True) -> ModelField:
    return ModelField(key=key, label=label, help_ja=help_ja, help_en=help_en, required=required)


MODEL_SETTINGS: dict[str, ModelSettingsSpec] = {
    "z-image": ModelSettingsSpec(
        profile_id="z-image",
        group_title="Z-Image / Z-Image-Turbo Model Paths",
        command_status="implemented",
        scripts=("zimage_train_network.py", "zimage_cache_latents.py", "zimage_cache_text_encoder_outputs.py"),
        fields=(
            field("zimage_dit", "Z-Image DiT", "Z-Imageの学習対象DiTです。BaseまたはDe-Turbo系を指定します。", "Z-Image DiT to train. Usually use Base or De-Turbo weights."),
            field("zimage_vae", "Z-Image VAE", "Z-Image用VAEファイルです。", "Z-Image VAE file."),
            field("zimage_text_encoder", "Z-Image text encoder", "Z-Image用Text Encoderです。", "Z-Image text encoder file."),
            field("zimage_base_weights", "Z-Image base weights", "任意設定です。必要な場合だけ指定します。", "Optional base weights. Set only when needed.", required=False),
        ),
    ),
    "wan2.2": ModelSettingsSpec(
        profile_id="wan2.2",
        group_title="Wan2.2 Model Paths",
        command_status="implemented",
        scripts=("wan_train_network.py", "wan_cache_latents.py", "wan_cache_text_encoder_outputs.py"),
        fields=(
            field("wan_vae", "Wan VAE", "Wan用VAEファイルです。例: Wan2.1_VAE.pth", "Wan VAE file. Example: Wan2.1_VAE.pth"),
            field("wan_t5", "Wan T5", "Wan用Text Encoder/T5ファイルです。例: models_t5_umt5-xxl-enc-bf16.pth", "Wan Text Encoder/T5 file."),
            field("wan_dit", "Wan2.2 DiT low noise", "Wan2.2のlow-noise側DiTです。t2v-A14Bの2系統DiT構成で必要です。", "Wan2.2 low-noise DiT. Required for t2v-A14B."),
            field("wan_dit_high_noise", "Wan2.2 DiT high noise", "Wan2.2のhigh-noise側DiTです。low-noise側とセットで必要です。", "Wan2.2 high-noise DiT. Required with the low-noise DiT."),
        ),
    ),
    "wan2.1": ModelSettingsSpec(
        profile_id="wan2.1",
        group_title="Wan2.1 Model Paths",
        scripts=("wan_train_network.py", "wan_cache_latents.py", "wan_cache_text_encoder_outputs.py"),
        fields=(
            field("wan21_vae", "Wan2.1 VAE", "Wan2.1用VAEファイルです。", "Wan2.1 VAE file."),
            field("wan21_t5", "Wan2.1 T5", "Wan2.1用Text Encoder/T5ファイルです。", "Wan2.1 Text Encoder/T5 file."),
            field("wan21_dit", "Wan2.1 DiT", "Wan2.1のDiTファイルです。", "Wan2.1 DiT file."),
        ),
    ),
    "wan-single-frame": ModelSettingsSpec(
        profile_id="wan-single-frame",
        group_title="Wan Single Frame Model Paths",
        scripts=("wan_train_network.py", "wan_cache_latents.py", "wan_cache_text_encoder_outputs.py"),
        fields=(
            field("wan_sf_vae", "Wan single-frame VAE", "Wan single-frame学習用VAEです。", "Wan single-frame VAE file."),
            field("wan_sf_t5", "Wan single-frame T5", "Wan single-frame学習用T5です。", "Wan single-frame T5 file."),
            field("wan_sf_dit", "Wan single-frame DiT", "Wan single-frame学習用DiTです。", "Wan single-frame DiT file."),
        ),
    ),
    "hunyuan-video": ModelSettingsSpec(
        profile_id="hunyuan-video",
        group_title="HunyuanVideo Model Paths",
        scripts=("hv_train_network.py",),
        fields=(
            field("hv_vae", "HunyuanVideo VAE", "HunyuanVideo用VAEです。", "HunyuanVideo VAE file."),
            field("hv_text_encoder", "HunyuanVideo text encoder", "HunyuanVideo用Text Encoderです。", "HunyuanVideo text encoder file."),
            field("hv_dit", "HunyuanVideo DiT", "HunyuanVideoの学習対象DiTです。", "HunyuanVideo DiT file."),
        ),
    ),
    "hunyuan-video-1.5": ModelSettingsSpec(
        profile_id="hunyuan-video-1.5",
        group_title="HunyuanVideo 1.5 Model Paths",
        scripts=("hv_1_5_train_network.py", "hv_1_5_cache_latents.py", "hv_1_5_cache_text_encoder_outputs.py"),
        fields=(
            field("hv15_vae", "HunyuanVideo 1.5 VAE", "HunyuanVideo 1.5用VAEです。", "HunyuanVideo 1.5 VAE file."),
            field("hv15_text_encoder", "HunyuanVideo 1.5 text encoder", "HunyuanVideo 1.5用Text Encoderです。", "HunyuanVideo 1.5 text encoder file."),
            field("hv15_dit", "HunyuanVideo 1.5 DiT", "HunyuanVideo 1.5の学習対象DiTです。", "HunyuanVideo 1.5 DiT file."),
        ),
    ),
    "framepack": ModelSettingsSpec(
        profile_id="framepack",
        group_title="FramePack Model Paths",
        scripts=("fpack_train_network.py", "fpack_cache_latents.py", "fpack_cache_text_encoder_outputs.py"),
        fields=(
            field("fpack_vae", "FramePack VAE", "FramePack用VAEです。", "FramePack VAE file."),
            field("fpack_text_encoder", "FramePack text encoder", "FramePack用Text Encoderです。", "FramePack text encoder file."),
            field("fpack_dit", "FramePack DiT", "FramePackの学習対象DiTです。", "FramePack DiT file."),
        ),
    ),
    "framepack-single-frame": ModelSettingsSpec(
        profile_id="framepack-single-frame",
        group_title="FramePack Single Frame Model Paths",
        scripts=("fpack_train_network.py", "fpack_cache_latents.py", "fpack_cache_text_encoder_outputs.py"),
        fields=(
            field("fpack_sf_vae", "FramePack single-frame VAE", "FramePack single-frame用VAEです。", "FramePack single-frame VAE file."),
            field("fpack_sf_text_encoder", "FramePack single-frame text encoder", "FramePack single-frame用Text Encoderです。", "FramePack single-frame text encoder file."),
            field("fpack_sf_dit", "FramePack single-frame DiT", "FramePack single-frameの学習対象DiTです。", "FramePack single-frame DiT file."),
        ),
    ),
    "flux-kontext": ModelSettingsSpec(
        profile_id="flux-kontext",
        group_title="FLUX.1 Kontext Model Paths",
        scripts=("flux_kontext_train_network.py", "flux_kontext_cache_latents.py", "flux_kontext_cache_text_encoder_outputs.py"),
        fields=(
            field("flux_kontext_vae", "FLUX.1 Kontext VAE", "FLUX.1 Kontext用VAEです。", "FLUX.1 Kontext VAE file."),
            field("flux_kontext_clip_l", "FLUX.1 Kontext CLIP-L", "FLUX.1 Kontext用CLIP-Lです。", "FLUX.1 Kontext CLIP-L file."),
            field("flux_kontext_t5", "FLUX.1 Kontext T5", "FLUX.1 Kontext用T5です。", "FLUX.1 Kontext T5 file."),
            field("flux_kontext_dit", "FLUX.1 Kontext DiT", "FLUX.1 Kontextの学習対象DiTです。", "FLUX.1 Kontext DiT file."),
        ),
    ),
    "flux2-dev": ModelSettingsSpec(
        profile_id="flux2-dev",
        group_title="FLUX.2 dev Model Paths",
        scripts=("flux_2_train_network.py", "flux_2_cache_latents.py", "flux_2_cache_text_encoder_outputs.py"),
        fields=(
            field("flux2_dev_vae", "FLUX.2 dev VAE", "FLUX.2 dev用VAEです。", "FLUX.2 dev VAE file."),
            field("flux2_dev_text_encoder", "FLUX.2 dev text encoder", "FLUX.2 dev用Text Encoderです。", "FLUX.2 dev text encoder file."),
            field("flux2_dev_dit", "FLUX.2 dev DiT", "FLUX.2 devの学習対象DiTです。", "FLUX.2 dev DiT file."),
        ),
    ),
    "flux2-klein": ModelSettingsSpec(
        profile_id="flux2-klein",
        group_title="FLUX.2 klein Model Paths",
        scripts=("flux_2_train_network.py", "flux_2_cache_latents.py", "flux_2_cache_text_encoder_outputs.py"),
        fields=(
            field("flux2_klein_vae", "FLUX.2 klein VAE", "FLUX.2 klein用VAEです。", "FLUX.2 klein VAE file."),
            field("flux2_klein_text_encoder", "FLUX.2 klein text encoder", "FLUX.2 klein用Text Encoderです。", "FLUX.2 klein text encoder file."),
            field("flux2_klein_dit", "FLUX.2 klein DiT", "FLUX.2 kleinの学習対象DiTです。", "FLUX.2 klein DiT file."),
        ),
    ),
    "qwen-image": ModelSettingsSpec(
        profile_id="qwen-image",
        group_title="Qwen-Image Model Paths",
        scripts=("qwen_image_train_network.py", "qwen_image_cache_latents.py", "qwen_image_cache_text_encoder_outputs.py"),
        fields=(
            field("qwen_image_vae", "Qwen-Image VAE", "Qwen-Image用VAEです。", "Qwen-Image VAE file."),
            field("qwen_image_text_encoder", "Qwen-Image text encoder", "Qwen-Image用Qwen2.5-VL Text Encoderです。", "Qwen-Image Qwen2.5-VL text encoder file."),
            field("qwen_image_dit", "Qwen-Image DiT", "Qwen-Imageの学習対象DiTです。", "Qwen-Image DiT file."),
        ),
    ),
    "hidream-o1": ModelSettingsSpec(
        profile_id="hidream-o1",
        group_title="HiDream-O1-Image Model Paths",
        scripts=("hidream_o1_train_network.py", "hidream_o1_cache_pixel.py", "hidream_o1_cache_text_encoder_outputs.py"),
        fields=(
            field("hidream_o1_vae", "HiDream-O1 VAE", "HiDream-O1用VAEです。", "HiDream-O1 VAE file."),
            field("hidream_o1_text_encoder", "HiDream-O1 text encoder", "HiDream-O1用Text Encoderです。", "HiDream-O1 text encoder file."),
            field("hidream_o1_dit", "HiDream-O1 DiT", "HiDream-O1の学習対象DiTです。", "HiDream-O1 DiT file."),
        ),
    ),
    "kandinsky5": ModelSettingsSpec(
        profile_id="kandinsky5",
        group_title="Kandinsky 5 Model Paths",
        scripts=("kandinsky5_train_network.py", "kandinsky5_cache_latents.py", "kandinsky5_cache_text_encoder_outputs.py"),
        fields=(
            field("kandinsky5_vae", "Kandinsky 5 VAE", "Kandinsky 5用VAEです。", "Kandinsky 5 VAE file."),
            field("kandinsky5_text_encoder", "Kandinsky 5 text encoder", "Kandinsky 5用Text Encoderです。", "Kandinsky 5 text encoder file."),
            field("kandinsky5_dit", "Kandinsky 5 DiT", "Kandinsky 5の学習対象DiTです。", "Kandinsky 5 DiT file."),
        ),
    ),
    "ideogram4": ModelSettingsSpec(
        profile_id="ideogram4",
        group_title="Ideogram4 Model Paths",
        scripts=("ideogram4_train_network.py", "ideogram4_cache_latents.py", "ideogram4_cache_text_encoder_outputs.py"),
        fields=(
            field("ideogram4_vae", "Ideogram4 VAE", "Ideogram4用VAEです。", "Ideogram4 VAE file."),
            field("ideogram4_text_encoder", "Ideogram4 text encoder", "Ideogram4用Text Encoderです。", "Ideogram4 text encoder file."),
            field("ideogram4_dit", "Ideogram4 DiT", "Ideogram4の学習対象DiTです。", "Ideogram4 DiT file."),
        ),
    ),
    "krea2": ModelSettingsSpec(
        profile_id="krea2",
        group_title="Krea 2 Model Paths",
        scripts=("krea2_train_network.py", "krea2_cache_latents.py", "krea2_cache_text_encoder_outputs.py"),
        fields=(
            field("krea2_vae", "Krea 2 VAE", "Krea 2用VAEです。", "Krea 2 VAE file."),
            field("krea2_text_encoder", "Krea 2 text encoder", "Krea 2用Text Encoderです。", "Krea 2 text encoder file."),
            field("krea2_dit", "Krea 2 DiT", "Krea 2の学習対象DiTです。", "Krea 2 DiT file."),
        ),
    ),
}


def settings_spec(profile_id: str) -> ModelSettingsSpec:
    return MODEL_SETTINGS.get(profile_id, MODEL_SETTINGS["z-image"])


def required_keys(profile_id: str) -> list[str]:
    return [f.key for f in settings_spec(profile_id).fields if f.required]


def optional_keys(profile_id: str) -> list[str]:
    return [f.key for f in settings_spec(profile_id).fields if not f.required]


def all_model_path_keys() -> list[str]:
    keys: list[str] = []
    for spec in MODEL_SETTINGS.values():
        for item in spec.fields:
            if item.key not in keys:
                keys.append(item.key)
    return keys


def scripts_for_profile(profile_id: str) -> tuple[str, ...]:
    return settings_spec(profile_id).scripts
