from __future__ import annotations

from pathlib import Path

from model_adapters import get_adapter
from model_registry import get_profile
from path_resolver import resolve_path

from model_file_format import resolve_model_file
from model_path_autofill_recursive import KEYS as ROLE_KEYS
from model_path_autofill_recursive import detect_paths, find_role, setting_value
from model_settings_catalog import optional_keys, required_keys


def detect_model_files(model_dir: Path, profile_id: str) -> dict[str, str]:
    """Detect the selected profile's model files under a folder the user picked.

    This used to be a Z-Image-only scorer that matched keywords against the file name
    and added points for "fp8" and "turbo". It found nothing in the official repository
    layout (whose files are named diffusion_pytorch_model-00001-of-00002.safetensors),
    and pointed at another model's weights entirely when given a ComfyUI tree. Both
    preferences were also backwards: musubi-tuner's docs say to train against Base
    rather than Turbo, and reject fp8_scaled weights for several models.

    It now reuses the same detection the rest of the app uses: the exact table for known
    repository layouts, then a role-based scan that prefers the first shard of a split
    set and never proposes a *.safetensors.index.json manifest.
    """
    wanted = required_keys(profile_id) + optional_keys(profile_id)
    root = resolve_path(model_dir)

    found = {key: value for key, value in detect_paths(root).items() if key in wanted}

    # detect_paths expects a models root containing per-model folders. When the user
    # picks the model folder itself, scan it directly for each remaining role.
    root_text = root.as_posix().lower()
    for key in wanted:
        if found.get(key):
            continue
        entry = ROLE_KEYS.get(key)
        if entry is None:
            continue
        hints, role = entry
        path = find_role(root, role)
        if path is None:
            continue
        # A role-only match is not evidence of the right model: pointed at a ComfyUI
        # tree, "the file that looks like a DiT" was another architecture entirely.
        # Require the model's name somewhere in the folder or the file path.
        candidate_text = path.as_posix().lower()
        if not any(h.lower() in root_text or h.lower() in candidate_text for h in hints):
            continue
        resolved = resolve_model_file(path)
        if resolved is not None:
            found[key] = setting_value(resolved.resolve())

    return {key: found.get(key, "") for key in wanted}


def _status_dir(key: str, value: str) -> str:
    if not value:
        return f"❌ {key}: not set"
    p = resolve_path(value)
    if not p.exists():
        return f"❌ {key}: not found: {p}  (settings: {value})"
    if not p.is_dir():
        return f"❌ {key}: not a directory: {p}  (settings: {value})"
    return f"✅ {key}: {p}  (settings: {value})"


def _status_file(key: str, value: str) -> str:
    if not value:
        return f"❌ {key}: not set"
    p = resolve_path(value)
    if not p.exists():
        return f"❌ {key}: not found: {p}  (settings: {value})"
    if not p.is_file():
        return f"❌ {key}: not a file: {p}  (settings: {value})"
    return f"✅ {key}: {p}  (settings: {value})"


def validate_settings_paths(values: dict[str, str], profile_id: str = "z-image") -> str:
    profile = get_profile(profile_id)
    required_dirs = ["musubi_repo", "datasets_dir", "outputs_dir", "comfyui_loras_dir"]
    required_files = ["musubi_python"]
    lines = ["# Settings Validation", "", f"Profile: {profile.display_name}", "", "Relative paths are resolved from the repository root.", ""]

    for key in required_dirs:
        lines.append(_status_dir(key, values.get(key, "")))
    for key in required_files:
        lines.append(_status_file(key, values.get(key, "")))

    try:
        adapter = get_adapter(profile.id)
        lines.append("")
        lines.append(f"## {profile.display_name} model paths")
        for key in adapter.required_setting_keys():
            lines.append(_status_file(key, values.get(key, "")))
        for key in adapter.optional_setting_keys():
            value = values.get(key, "")
            if value:
                lines.append(_status_file(key, value))
            else:
                lines.append(f"ℹ️ {key}: optional / not set")
    except NotImplementedError as exc:
        lines.append(f"❌ {exc}")

    repo_value = values.get("musubi_repo", "")
    repo = resolve_path(repo_value) if repo_value else Path("")
    if repo.exists():
        src = repo / "src" / "musubi_tuner"
        if src.exists():
            lines.append(f"✅ musubi source: {src}")
        else:
            lines.append(f"❌ musubi source not found: {src}")

    text = "\n".join(lines)
    if "❌" in text:
        text += "\n\nResult: ❌ 不足があります。Browseで指定し直してください。"
    else:
        text += "\n\nResult: ✅ Settings looks good. Save Settingsしてください。"
    return text
