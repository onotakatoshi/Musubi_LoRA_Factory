from __future__ import annotations

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
python -m musubi_tuner.zimage_train_network --dataset_config dataset.toml
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
    print("Command preview test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
