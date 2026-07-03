from __future__ import annotations

import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from PIL import Image

from caption_editor import bulk_replace_caption_rows, load_caption_rows, remove_words_caption_rows, save_caption_rows
from command_preview import preview_from_settings
from pipeline import build_dataset_toml, check_dataset


def write_test_settings(path: Path, musubi_repo: Path) -> None:
    path.write_text(
        f"""
[musubi]
repo_path = "{musubi_repo}"
python_path = "python"

[paths]
datasets_dir = "/tmp/datasets/lora"
outputs_dir = "/tmp/outputs/lora"
comfyui_loras_dir = "/tmp/ComfyUI/models/loras"

[caption]
mode = "manual"
joycaption_command = ""
llm_endpoint = ""
llm_model = ""

[model_paths]
zimage_dit = "/tmp/models/z-image/z_image_base_or_deturbo.safetensors"
zimage_vae = "/tmp/models/z-image/ae.safetensors"
zimage_text_encoder = "/tmp/models/z-image/text_encoder.safetensors"
zimage_base_weights = ""
wan_vae = "/tmp/models/wan/vae.pth"
wan_t5 = "/tmp/models/wan/t5.pth"
wan_dit = "/tmp/models/wan/dit.safetensors"
wan_dit_high_noise = "/tmp/models/wan/dit_high_noise.safetensors"
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dataset = root / "dataset"
        output = root / "output"
        musubi_repo = root / "musubi-tuner"
        (musubi_repo / "src" / "musubi_tuner").mkdir(parents=True)
        dataset.mkdir()

        img = dataset / "sample.png"
        Image.new("RGB", (512, 512), color=(128, 128, 128)).save(img)
        img.with_suffix(".txt").write_text("blue eyes, hair, background\n", encoding="utf-8")

        check = check_dataset(dataset)
        assert "画像数: 1" in check

        rows = load_caption_rows(dataset)
        rows = remove_words_caption_rows(rows, "hair, background")
        rows = bulk_replace_caption_rows(rows, "blue", "green")
        saved = save_caption_rows(dataset, rows)
        assert "保存完了" in saved
        assert "green eyes" in img.with_suffix(".txt").read_text(encoding="utf-8")

        dataset_toml = Path(build_dataset_toml(dataset, output, 512))
        assert dataset_toml.exists()

        settings = root / "settings.toml"
        write_test_settings(settings, musubi_repo)
        preview = preview_from_settings(
            settings_path=settings,
            dataset_toml=str(dataset_toml),
            target_model="z-image",
            rank=16,
            alpha=16,
            epochs=1,
            lr=0.00005,
            output_name="smoke_zimage",
            task="z-image",
        )
        assert "cd " in preview
        assert "zimage_cache_latents.py" in preview
        assert "zimage_train_network.py" in preview

    print("Smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
