from __future__ import annotations

import tempfile
from pathlib import Path

from command_path_guard import command_paths_ok, validate_command_paths


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dataset = root / "dataset.toml"
        vae = root / "ae.safetensors"
        dit = root / "dit.safetensors"
        text = root / "text_encoder.safetensors"
        output = root / "output"
        output.mkdir()
        for p in [dataset, vae, dit, text]:
            p.write_text("dummy", encoding="utf-8")

        sections = {
            "latent_cache": f"python zimage_cache_latents.py --dataset_config {dataset} --vae {vae}",
            "text_cache": f"python zimage_cache_text_encoder_outputs.py --dataset_config {dataset} --text_encoder {text}",
            "train": f"python zimage_train_network.py --dataset_config {dataset} --vae {vae} --dit {dit} --text_encoder {text} --output_dir {output / 'run'}",
        }
        ok, report = command_paths_ok(sections)
        assert ok, report
        assert "Result: OK" in report

        bad_sections = dict(sections)
        bad_sections["train"] = bad_sections["train"].replace(str(dit), str(root / "missing_dit.safetensors"))
        ok, report = command_paths_ok(bad_sections)
        assert not ok
        assert "missing_dit" in report
        assert "Result: NG" in report

        parse_bad = {"latent_cache": "python x --dataset_config 'broken", "text_cache": sections["text_cache"], "train": sections["train"]}
        assert "parse error" in validate_command_paths(parse_bad)

    print("Command path guard test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
