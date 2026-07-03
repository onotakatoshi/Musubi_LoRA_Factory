from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import toml

from model_adapters import get_adapter
from model_registry import get_profile
from musubi_runtime_check import check_musubi_runtime
from verification_readiness import verification_readiness


def _path_status(label: str, value: str, must_exist: bool = True) -> str:
    if not value:
        return f"❌ {label}: not set"
    p = Path(value)
    if must_exist and not p.exists():
        return f"❌ {label}: not found: {p}"
    return f"✅ {label}: {p}"


def _run_version(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
    except FileNotFoundError:
        return "not found"
    except subprocess.TimeoutExpired:
        return "timeout"
    first = (proc.stdout or "").splitlines()
    return first[0] if first else f"exit code {proc.returncode}"


def _check_musubi_scripts(repo: Path, profile_id: str) -> list[str]:
    src = repo / "src" / "musubi_tuner"
    lines = [_path_status("src/musubi_tuner", str(src))]
    if profile_id == "z-image":
        lines.append(_path_status("zimage_train_network.py", str(src / "zimage_train_network.py")))
        lines.append(_path_status("zimage_cache_latents.py", str(src / "zimage_cache_latents.py")))
        lines.append(_path_status("zimage_cache_text_encoder_outputs.py", str(src / "zimage_cache_text_encoder_outputs.py")))
    else:
        lines.append(f"ℹ️ script check for {profile_id}: not implemented yet")
    return lines


def check_environment(settings_path: Path, profile_id: str = "z-image") -> str:
    profile = get_profile(profile_id)
    lines = ["# Environment Check", "", f"Profile: {profile.display_name}", ""]
    lines.append(f"GUI Python: {sys.version.split()[0]}")
    lines.append(f"nvidia-smi: {_run_version(['nvidia-smi'])}")
    lines.append("")

    lines.append("## Verification readiness")
    lines.append(verification_readiness())
    lines.append("")

    if not settings_path.exists():
        lines.append(f"❌ settings.toml not found: {settings_path}")
        lines.append("次: configs/settings.example.toml を configs/settings.toml にコピーして編集してください。")
        return "\n".join(lines)

    data = toml.load(settings_path)
    musubi = data.get("musubi", {})
    model_paths = data.get("model_paths", {})
    paths = data.get("paths", {})

    lines.append("## musubi-tuner")
    lines.append(_path_status("repo_path", musubi.get("repo_path", "")))
    lines.append(_path_status("python_path", musubi.get("python_path", "")))
    repo = Path(musubi.get("repo_path", "")) if musubi.get("repo_path") else None
    if repo:
        lines.extend(_check_musubi_scripts(repo, profile.id))
    lines.append("")

    if musubi.get("repo_path") and musubi.get("python_path"):
        lines.append("## musubi runtime")
        lines.append(check_musubi_runtime(musubi.get("python_path", ""), musubi.get("repo_path", ""), profile.id))
        lines.append("")

    try:
        adapter = get_adapter(profile.id)
        lines.append(f"## {profile.display_name} model files")
        for key in adapter.required_setting_keys():
            lines.append(_path_status(key, model_paths.get(key, "")))
        for key in adapter.optional_setting_keys():
            value = model_paths.get(key, "")
            if value:
                lines.append(_path_status(key, value))
            else:
                lines.append(f"ℹ️ {key}: optional / not set")
    except NotImplementedError as exc:
        lines.append(f"❌ {exc}")
    lines.append("")

    lines.append("## Output paths")
    lines.append(_path_status("datasets_dir", paths.get("datasets_dir", ""), must_exist=False))
    lines.append(_path_status("outputs_dir", paths.get("outputs_dir", ""), must_exist=False))
    lines.append(_path_status("comfyui_loras_dir", paths.get("comfyui_loras_dir", ""), must_exist=False))
    lines.append("")

    text = "\n".join(lines)
    if "❌" in text or "Result: NG" in text or "NOT READY:" in text:
        text += "\n\nResult: ❌ 不足があります。上の❌/NG/NOT READYを直してからGUIでPreflight Checkしてください。"
    else:
        text += f"\n\nResult: ✅ {profile.display_name} LoRA作成の前提ファイルと実行環境は揃っています。"
    return text


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(check_environment(root / "configs" / "settings.toml"))
