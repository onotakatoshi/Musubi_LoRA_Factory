from __future__ import annotations

import tempfile
from pathlib import Path

from command_path_guard import command_paths_ok, validate_command_paths


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        repo = root / "musubi-tuner"
        script_dir = repo / "src" / "musubi_tuner"
        script_dir.mkdir(parents=True)
        python_path = root / "venv" / "bin" / "python"
        python_path.parent.mkdir(parents=True)
        python_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
        for name in ["zimage_cache_latents.py", "zimage_cache_text_encoder_outputs.py", "zimage_train_network.py"]:
            (script_dir / name).write_text("# dummy\n", encoding="utf-8")

        dataset = root / "dataset.toml"
        vae = root / "ae.safetensors"
        dit = root / "dit.safetensors"
        text = root / "text_encoder.safetensors"
        output = root / "output"
        output.mkdir()
        for p in [dataset, vae, dit, text]:
            p.write_text("dummy", encoding="utf-8")

        sections = {
            "latent_cache": f"cd {repo} && {python_path} src/musubi_tuner/zimage_cache_latents.py --dataset_config {dataset} --vae {vae}",
            "text_cache": f"cd {repo} && {python_path} src/musubi_tuner/zimage_cache_text_encoder_outputs.py --dataset_config {dataset} --text_encoder {text}",
            "train": f"cd {repo} && {python_path} -m accelerate.commands.launch src/musubi_tuner/zimage_train_network.py --dataset_config {dataset} --vae {vae} --dit {dit} --text_encoder {text} --output_dir {output / 'run'}",
        }
        ok, report = command_paths_ok(sections)
        assert ok, report
        assert "OK: cwd" in report
        assert "OK: python" in report
        assert "OK: script" in report
        assert "Result: OK" in report

        bad_sections = dict(sections)
        bad_sections["train"] = bad_sections["train"].replace(str(dit), str(root / "missing_dit.safetensors"))
        ok, report = command_paths_ok(bad_sections)
        assert not ok
        assert "missing_dit" in report
        assert "Result: NG" in report

        bad_python = dict(sections)
        bad_python["latent_cache"] = bad_python["latent_cache"].replace(str(python_path), str(root / "missing_python"))
        ok, report = command_paths_ok(bad_python)
        assert not ok
        assert "python not found" in report

        bad_script = dict(sections)
        bad_script["text_cache"] = bad_script["text_cache"].replace("zimage_cache_text_encoder_outputs.py", "missing_script.py")
        ok, report = command_paths_ok(bad_script)
        assert not ok
        assert "script not found" in report

        parse_bad = {"latent_cache": "python x --dataset_config 'broken", "text_cache": sections["text_cache"], "train": sections["train"]}
        assert "parse error" in validate_command_paths(parse_bad)

    print("Command path guard test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
