from __future__ import annotations

from model_registry import ModelProfile, enabled_profiles, get_profile, normalize_profile_id

WIRED_PROFILE_IDS = {
    "z-image",
    "wan2.2-t2v-a14b",
    "wan2.2-i2v-a14b",
    "wan2.2-ti2v-5b",
    "wan2.1",
    "hunyuan-video",
    "flux-kontext",
    "flux2-dev",
    "flux2-klein",
    "qwen-image",
    "minimax-h3",
    "krea2",
}


def _wired_profiles() -> list[ModelProfile]:
    return [profile for profile in enabled_profiles(include_future=True) if profile.id in WIRED_PROFILE_IDS]


def available_model_ids(include_future: bool = False) -> list[str]:
    profiles = enabled_profiles(include_future=True) if include_future else _wired_profiles()
    return [profile.id for profile in profiles]


def available_model_labels(include_future: bool = False) -> list[str]:
    profiles = enabled_profiles(include_future=True) if include_future else _wired_profiles()
    return [profile.display_name for profile in profiles]


def label_for_profile(profile_id: str) -> str:
    profile = get_profile(profile_id)
    if profile.id not in WIRED_PROFILE_IDS:
        return get_profile("z-image").display_name
    return profile.display_name


def profile_id_from_label(label: str) -> str:
    for profile in enabled_profiles(include_future=True):
        if profile.display_name == label:
            if profile.id in WIRED_PROFILE_IDS:
                return profile.id
            return get_profile("z-image").id
    return get_profile("z-image").id


def current_profile_id(settings: dict) -> str:
    """Profile the app should open with, from settings, falling back to the default."""
    configured = normalize_profile_id(str(settings.get("ui", {}).get("target_model", "") or "").strip())
    if configured in WIRED_PROFILE_IDS:
        return configured
    return v1_default_profile().id


def default_project_name(profile_id: str) -> str:
    """Slug for the default output folder and LoRA name.

    The Z-Image-era literals ("Eye_Blue_v1", "eye_lora_zimage") stayed behind when the
    app grew to eleven models and read as leftovers from someone else's project.
    """
    return f"{normalize_profile_id(profile_id)}_lora"


def task_for_profile(profile_id: str) -> str:
    return get_profile(profile_id).task


def help_for_profile(profile_id: str, lang: str = "日本語") -> str:
    profile = get_profile(profile_id)
    description = profile.description_en if lang == "English" else profile.description_ja
    if lang == "English":
        return f"{profile.display_name}\n\nProfile ID: {profile.id}\nTask: {profile.task}\n\n{description}"
    return f"{profile.display_name}\n\nProfile ID: {profile.id}\nTask: {profile.task}\n\n{description}"


def v1_default_profile() -> ModelProfile:
    profiles = _wired_profiles()
    if not profiles:
        raise RuntimeError("No wired model profiles")
    return profiles[0]
