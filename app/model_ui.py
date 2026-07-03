from __future__ import annotations

from model_registry import ModelProfile, enabled_profiles, get_profile


def available_model_ids(include_future: bool = False) -> list[str]:
    return [profile.id for profile in enabled_profiles(include_future=include_future)]


def available_model_labels(include_future: bool = False) -> list[str]:
    return [profile.display_name for profile in enabled_profiles(include_future=include_future)]


def label_for_profile(profile_id: str) -> str:
    return get_profile(profile_id).display_name


def profile_id_from_label(label: str) -> str:
    for profile in enabled_profiles(include_future=True):
        if profile.display_name == label:
            return profile.id
    return get_profile("z-image").id


def task_for_profile(profile_id: str) -> str:
    return get_profile(profile_id).task


def help_for_profile(profile_id: str, lang: str = "日本語") -> str:
    profile = get_profile(profile_id)
    description = profile.description_en if lang == "English" else profile.description_ja
    if lang == "English":
        return f"{profile.display_name}\n\nProfile ID: {profile.id}\nTask: {profile.task}\n\n{description}"
    return f"{profile.display_name}\n\nProfile ID: {profile.id}\nTask: {profile.task}\n\n{description}"


def v1_default_profile() -> ModelProfile:
    profiles = enabled_profiles(include_future=False)
    if not profiles:
        raise RuntimeError("No enabled model profiles")
    return profiles[0]
