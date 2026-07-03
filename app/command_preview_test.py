from __future__ import annotations

from pathlib import Path

from commands import ModelPaths, build_zimage_preview
from runner import split_command_sections, validate_command_preview


VALID_PREVIEW = """
# Command Preview

# 1. Latent cache
cd /tmp/project
python -m musubi_tuner.zimage_cache_latents --dataset_config dataset.toml

# 2. Text encoder cache
cd /tmp/project
python -m musubi_tuner.zimage_cache_text_encoder_outputs --dataset_config dataset.toml

# 3. Train LoRA
cd /tmp/project
python -m accelerate.commands.launch src/musubi_tuner/zimage_train_network.py --dataset_config dataset.toml
""".strip()


def main() -> int:
    assert validate_command_preview("").startswith("NG:")
    assert validate_command_preview("NG: broken").startswith("NG:")
    assert validate_command_preview(VALID_PREVIEW).startswith("OK:")
    sections = split_command_sections(VALID_PREVIEW)
    assert set(sections) == {"latent_cache", "text_cache", "train"}
    assert "zimage_cache_latents" in sections["latent_cache"]
    assert "zimage_cache_text_encoder_outputs" in sections["text_cache"]
    assert "zimage_train_network" in sections["train"]

    generated = build_zimage_preview(
        musubi_python=Path("/opt/musubi/.venv/bin/python"),
        musubi_repo=Path("/opt/musubi"),
        dataset_toml=Path("/tmp/dataset.toml"),
        output_dir=Path("/tmp/output"),
        output_name="eye_lora_zimage",
        paths=ModelPaths(vae="/models/ae.safetensors", dit="/models/dit.safetensors", text_encoder="/models/text.safetensors"),
        rank=16,
        alpha=16,
        epochs=1,
        lr=0.00005,
    )
    generated_sections = split_command_sections(generated)
    assert "/opt/musubi/.venv/bin/python" in generated_sections["latent_cache"]
    assert "/opt/musubi/.venv/bin/python" in generated_sections["text_cache"]
    assert "/opt/musubi/.venv/bin/python -m accelerate.commands.launch" in generated_sections["train"]
    assert "accelerate launch" not in generated_sections["train"]

    print("Command preview test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
