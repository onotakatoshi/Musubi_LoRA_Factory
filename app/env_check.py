from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import toml


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


def check_environment(settings_path: Path) -> str:
    lines = ["# Environment Check", ""]
    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append(f"nvidia-smi: {_run_version(['nvidia-smi'])}")
    lines.append(f"accelerate: {_run_version(['accelerate', '--version'])}")
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
        lines.append(_path_status("src/musubi_tuner", str(repo / "src" / "musubi_tuner")))
        lines.append(_path_status("zimage_train_network.py", str(repo / "src" / "musubi_tuner" / "zimage_train_network.py")))
        lines.append(_path_status("zimage_cache_latents.py", str(repo / "src" / "musubi_tuner" / "zimage_cache_latents.py")))
        lines.append(_path_status("zimage_cache_text_encoder_outputs.py", str(repo / "src" / "musubi_tuner" / "zimage_cache_text_encoder_outputs.py")))
    lines.append("")

    lines.append("## Z-Image model files")
    lines.append(_path_status("zimage_dit", model_paths.get("zimage_dit", "")))
    lines.append(_path_status("zimage_vae", model_paths.get("zimage_vae", "")))
    lines.append(_path_status("zimage_text_encoder", model_paths.get("zimage_text_encoder", "")))
    base_weights = model_paths.get("zimage_base_weights", "")
    if base_weights:
        lines.append(_path_status("zimage_base_weights", base_weights))
    else:
        lines.append("ℹ️ zimage_base_weights: optional / not set")
    lines.append("")

    lines.append("## Output paths")
    lines.append(_path_status("datasets_dir", paths.get("datasets_dir", ""), must_exist=False))
    lines.append(_path_status("outputs_dir", paths.get("outputs_dir", ""), must_exist=False))
    lines.append(_path_status("comfyui_loras_dir", paths.get("comfyui_loras_dir", ""), must_exist=False))
    lines.append("")

    text = "\n".join(lines)
    if "❌" in text:
        text += "\n\nResult: ❌ 不足があります。上の❌を直してからGUIでPreflight Checkしてください。"
    else:
        text += "\n\nResult: ✅ Z-Image LoRA作成の前提ファイルは揃っています。"
    return text


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(check_environment(root / "configs" / "settings.toml"))
