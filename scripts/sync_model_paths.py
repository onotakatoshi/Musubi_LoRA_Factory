#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    import toml
except ImportError as exc:
    raise SystemExit("toml is required. Run: python3 -m pip install toml") from exc

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"
SETTINGS_EXAMPLE_PATH = ROOT / "configs" / "settings.example.toml"

MODEL_EXTS = {".safetensors", ".pth", ".pt", ".bin", ".json"}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def repo_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def as_setting(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def find_existing(*candidates: Path) -> str:
    for candidate in candidates:
        if candidate.exists():
            return as_setting(candidate)
    return ""


def files_under(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file() and (p.suffix.lower() in MODEL_EXTS or p.name.endswith(".index.json"))]


def score(path: Path, keywords: Iterable[str], avoid: Iterable[str] = ()) -> int:
    text = str(path).lower()
    value = 0
    for keyword in keywords:
        if keyword.lower() in text:
            value += 10
    for keyword in avoid:
        if keyword.lower() in text:
            value -= 20
    if path.name.endswith(".index.json"):
        value += 5
    if path.suffix.lower() == ".safetensors":
        value += 3
    if path.suffix.lower() in {".pth", ".pt"}:
        value += 2
    return value


def best_file(root: Path, keywords: Iterable[str], avoid: Iterable[str] = ()) -> str:
    candidates = []
    for item in files_under(root):
        s = score(item, keywords, avoid)
        if s > 0:
            candidates.append((s, len(str(item)), item))
    if not candidates:
        return ""
    candidates.sort(key=lambda x: (-x[0], x[1]))
    return as_setting(candidates[0][2])


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        return toml.load(SETTINGS_PATH)
    if SETTINGS_EXAMPLE_PATH.exists():
        return toml.load(SETTINGS_EXAMPLE_PATH)
    return {}


def backup_settings() -> None:
    if SETTINGS_PATH.exists():
        backup = SETTINGS_PATH.with_suffix(f".toml.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(SETTINGS_PATH, backup)
        print(f"Backup: {backup}")


def set_if_found(paths: dict, key: str, value: str, *, overwrite: bool) -> bool:
    if not value:
        return False
    old = str(paths.get(key, "") or "")
    if old and not overwrite:
        return False
    paths[key] = value
    if old != value:
        print(f"SET {key} = {value}")
    return old != value


def sync_known_roots(paths: dict, models_dir: Path, overwrite: bool) -> int:
    changed = 0

    z = models_dir / "z-image" / "Tongyi-MAI" / "Z-Image"
    changed += set_if_found(paths, "zimage_dit", find_existing(z / "transformer" / "diffusion_pytorch_model-00001-of-00002.safetensors", Path(best_file(z / "transformer", ["diffusion", "model"], ["vae", "text_encoder"]))), overwrite=overwrite)
    changed += set_if_found(paths, "zimage_vae", find_existing(z / "vae" / "diffusion_pytorch_model.safetensors", Path(best_file(z / "vae", ["vae", "diffusion"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "zimage_text_encoder", find_existing(z / "text_encoder" / "model-00001-of-00003.safetensors", Path(best_file(z / "text_encoder", ["model", "text", "encoder"]))) , overwrite=overwrite)

    wan_t2v = models_dir / "wan" / "Wan2.2-T2V-A14B"
    changed += set_if_found(paths, "wan_vae", find_existing(wan_t2v / "Wan2.1_VAE.pth", Path(best_file(wan_t2v, ["vae"], ["dit", "diffusion"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan_t5", find_existing(wan_t2v / "models_t5_umt5-xxl-enc-bf16.pth", Path(best_file(wan_t2v, ["t5", "umt5"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan_dit", find_existing(wan_t2v / "low_noise_model" / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan_t2v / "low_noise_model", ["diffusion", "model"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan_dit_high_noise", find_existing(wan_t2v / "high_noise_model" / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan_t2v / "high_noise_model", ["diffusion", "model"]))) , overwrite=overwrite)

    wan_i2v = models_dir / "wan" / "Wan2.2-I2V-A14B"
    changed += set_if_found(paths, "wan22_i2v_vae", find_existing(wan_i2v / "Wan2.1_VAE.pth", Path(best_file(wan_i2v, ["vae"], ["dit", "diffusion"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan22_i2v_t5", find_existing(wan_i2v / "models_t5_umt5-xxl-enc-bf16.pth", Path(best_file(wan_i2v, ["t5", "umt5"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan22_i2v_dit", find_existing(wan_i2v / "low_noise_model" / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan_i2v / "low_noise_model", ["diffusion", "model"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan22_i2v_dit_high_noise", find_existing(wan_i2v / "high_noise_model" / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan_i2v / "high_noise_model", ["diffusion", "model"]))) , overwrite=overwrite)

    wan_ti2v = models_dir / "wan" / "Wan2.2-TI2V-5B"
    changed += set_if_found(paths, "wan22_ti2v_vae", find_existing(wan_ti2v / "Wan2.2_VAE.pth", wan_ti2v / "Wan2.1_VAE.pth", Path(best_file(wan_ti2v, ["vae"], ["dit", "diffusion"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan22_ti2v_t5", find_existing(wan_ti2v / "models_t5_umt5-xxl-enc-bf16.pth", Path(best_file(wan_ti2v, ["t5", "umt5"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan22_ti2v_dit", find_existing(wan_ti2v / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan_ti2v, ["diffusion", "model", "dit"], ["vae", "t5", "text_encoder"]))) , overwrite=overwrite)

    wan21 = models_dir / "wan" / "Wan2.1-T2V-14B"
    changed += set_if_found(paths, "wan21_vae", find_existing(wan21 / "Wan2.1_VAE.pth", Path(best_file(wan21, ["vae"], ["dit", "diffusion"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan21_t5", find_existing(wan21 / "models_t5_umt5-xxl-enc-bf16.pth", Path(best_file(wan21, ["t5", "umt5"]))) , overwrite=overwrite)
    changed += set_if_found(paths, "wan21_dit", find_existing(wan21 / "diffusion_pytorch_model.safetensors.index.json", Path(best_file(wan21, ["diffusion", "model", "dit"], ["vae", "t5"]))) , overwrite=overwrite)

    qwen = models_dir / "qwen" / "Qwen-Image"
    changed += set_if_found(paths, "qwen_image_vae", best_file(qwen, ["vae"], ["diffusion", "dit", "text_encoder"]), overwrite=overwrite)
    changed += set_if_found(paths, "qwen_image_text_encoder", best_file(qwen, ["text_encoder", "qwen", "vl"], ["vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "qwen_image_dit", best_file(qwen, ["diffusion", "transformer", "dit"], ["vae", "text_encoder"]), overwrite=overwrite)

    hv = models_dir / "hunyuan-video" / "HunyuanVideo"
    changed += set_if_found(paths, "hv_vae", best_file(hv, ["vae"], ["dit", "text_encoder"]), overwrite=overwrite)
    changed += set_if_found(paths, "hv_text_encoder", best_file(hv, ["text_encoder", "llava", "clip", "encoder"], ["vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "hv_dit", best_file(hv, ["dit", "transformer", "mp_rank", "model"], ["vae", "text_encoder", "clip"]), overwrite=overwrite)

    flux_k = models_dir / "flux" / "FLUX.1-Kontext-dev"
    changed += set_if_found(paths, "flux_kontext_vae", best_file(flux_k, ["ae", "vae"], ["text", "clip", "t5", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux_kontext_clip_l", best_file(flux_k, ["clip_l", "clip"], ["t5", "vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux_kontext_t5", best_file(flux_k, ["t5", "xxl"], ["vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux_kontext_dit", best_file(flux_k, ["flux", "diffusion", "transformer", "dit"], ["vae", "t5", "clip"]), overwrite=overwrite)

    flux2_dev = models_dir / "flux" / "FLUX.2-dev"
    changed += set_if_found(paths, "flux2_dev_vae", best_file(flux2_dev, ["ae", "vae"], ["text", "clip", "t5", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux2_dev_text_encoder", best_file(flux2_dev, ["text_encoder", "t5", "clip"], ["vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux2_dev_dit", best_file(flux2_dev, ["flux", "diffusion", "transformer", "dit"], ["vae", "text_encoder", "t5", "clip"]), overwrite=overwrite)

    flux2_klein = models_dir / "flux" / "FLUX.2-klein"
    changed += set_if_found(paths, "flux2_klein_vae", best_file(flux2_klein, ["ae", "vae"], ["text", "clip", "t5", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux2_klein_text_encoder", best_file(flux2_klein, ["text_encoder", "t5", "clip"], ["vae", "diffusion"]), overwrite=overwrite)
    changed += set_if_found(paths, "flux2_klein_dit", best_file(flux2_klein, ["flux", "diffusion", "transformer", "dit"], ["vae", "text_encoder", "t5", "clip"]), overwrite=overwrite)

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync downloaded model files into configs/settings.toml")
    parser.add_argument("--models-dir", default=str(Path.home() / "models"), help="Model download root. Default: ~/models")
    parser.add_argument("--settings", default=str(SETTINGS_PATH), help="settings.toml path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing non-empty model_paths values")
    parser.add_argument("--dry-run", action="store_true", help="Show detected changes without writing settings.toml")
    args = parser.parse_args()

    global SETTINGS_PATH
    SETTINGS_PATH = Path(args.settings).expanduser().resolve()
    models_dir = Path(args.models_dir).expanduser().resolve()

    data = load_settings()
    data.setdefault("model_paths", {})
    model_paths = data["model_paths"]

    print(f"Models dir: {models_dir}")
    print(f"Settings:   {SETTINGS_PATH}")
    print(f"Overwrite:  {args.overwrite}")
    print("")

    before = dict(model_paths)
    changed = sync_known_roots(model_paths, models_dir, args.overwrite)

    if args.dry_run:
        print("")
        print(f"Dry run: {changed} changes detected. settings.toml was not written.")
        return 0

    if changed:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        backup_settings()
        SETTINGS_PATH.write_text(toml.dumps(data), encoding="utf-8")
        print("")
        print(f"Wrote: {SETTINGS_PATH}")
        print(f"Changed keys: {changed}")
    else:
        print("No changes. Existing settings already look filled, or files were not found.")

    empty_after = [key for key, value in data.get("model_paths", {}).items() if not str(value or "").strip()]
    if empty_after:
        print("")
        print("Still empty keys:")
        for key in empty_after:
            print(f"  - {key}")
        print("These may belong to models that were not downloaded or whose repository layout needs a custom detector.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
