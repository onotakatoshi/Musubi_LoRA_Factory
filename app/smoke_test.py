from __future__ import annotations

import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from PIL import Image

from caption_diagnostics import diagnose_captions
from caption_editor import bulk_replace_caption_rows, load_caption_rows, remove_words_caption_rows, save_caption_rows
from command_preview import preview_from_settings
from i18n import normalize_language, tr
from model_adapters import ADAPTERS, CatalogAdapter, adapter_ids, get_adapter
from model_registry import ALIASES, PROFILES, enabled_profiles, get_profile, normalize_profile_id, profile_ids, profile_summary
from model_settings_catalog import MODEL_SETTINGS
from model_ui import WIRED_PROFILE_IDS, available_model_ids
from pipeline import build_dataset_toml, check_dataset
from preflight import run_preflight
from project_io import load_project, project_data, save_project
from recommended_defaults import DEFAULTS, help_text, status_text
from training_estimator import estimate_training_load
from training_presets import get_preset, preset_summary
from training_review import training_review


def write_test_settings(path: Path, musubi_repo: Path) -> None:
    path.write_text(
        f"""
[ui]
language = "日本語"

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


def write_existing_path_settings(path: Path, musubi_repo: Path, model_dir: Path) -> None:
    z_dit = model_dir / "z_image_base_or_deturbo.safetensors"
    z_vae = model_dir / "ae.safetensors"
    z_text = model_dir / "text_encoder.safetensors"
    for p in [z_dit, z_vae, z_text]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("dummy", encoding="utf-8")
    path.write_text(
        f"""
[ui]
language = "日本語"

[musubi]
repo_path = "{musubi_repo}"
python_path = "{sys.executable}"

[paths]
datasets_dir = "{model_dir.parent / 'datasets'}"
outputs_dir = "{model_dir.parent / 'outputs'}"
comfyui_loras_dir = "{model_dir.parent / 'ComfyUI' / 'models' / 'loras'}"

[caption]
mode = "manual"
joycaption_command = ""
llm_endpoint = ""
llm_model = ""

[model_paths]
zimage_dit = "{z_dit}"
zimage_vae = "{z_vae}"
zimage_text_encoder = "{z_text}"
zimage_base_weights = ""
""".strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    assert normalize_language(None) == "日本語"
    assert tr("日本語", "tab_settings") == "設定"
    assert tr("English", "tab_settings") == "Settings"
    assert "推奨デフォルト" in status_text("rank", DEFAULTS["rank"], "日本語")
    assert "ユーザー設定" in status_text("rank", 32, "日本語")
    assert "Recommended default" in status_text("lr", DEFAULTS["lr"], "English")
    assert "0.00005" in help_text("lr", "日本語")
    assert get_preset("eye").rank == 16
    assert "Rank=16" in preset_summary("eye", "日本語")
    assert "z-image" in profile_ids()
    assert get_profile("z-image").enabled_in_v1 is True
    assert "Z-Image" in profile_summary("z-image", "日本語")
    assert normalize_profile_id("wan2.2") == "wan2.2-t2v-a14b", "the legacy wan2.2 id must still resolve"
    assert ALIASES["wan2.2"] == "wan2.2-t2v-a14b"

    # Every registered profile needs a settings spec and an adapter, and the Target model
    # list must only offer profiles that actually have one.
    assert set(PROFILES) == set(MODEL_SETTINGS), "registry and settings catalog are out of sync"
    assert set(PROFILES) == set(adapter_ids()), "registry and adapters are out of sync"
    assert WIRED_PROFILE_IDS <= set(PROFILES), "Target model list offers an unknown profile"
    assert set(available_model_ids()) == WIRED_PROFILE_IDS
    assert available_model_ids()[0] == "z-image"

    # A profile with a real command builder must not be left out of the Target model list.
    implemented = {pid for pid, adapter in ADAPTERS.items() if type(adapter) is not CatalogAdapter}
    assert implemented <= WIRED_PROFILE_IDS, f"implemented but not selectable: {sorted(implemented - WIRED_PROFILE_IDS)}"
    for pid in implemented:
        assert MODEL_SETTINGS[pid].command_status == "implemented", f"{pid} has a builder but is marked catalog_only"
    for pid in WIRED_PROFILE_IDS - implemented:
        assert MODEL_SETTINGS[pid].command_status == "catalog_only", f"{pid} has no builder but is marked implemented"

    assert get_adapter("z-image").validate_model_paths({}) == ["model_paths.zimage_dit", "model_paths.zimage_vae", "model_paths.zimage_text_encoder"]
    assert get_adapter("minimax-h3").validate_model_paths({}) == [
        "model_paths.minimax_h3_dit",
        "model_paths.minimax_h3_text_encoder",
        "model_paths.minimax_h3_video_vae",
        "model_paths.minimax_h3_audio_vae",
    ]

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
        dup = dataset / "sample_dup.png"
        Image.new("RGB", (512, 512), color=(128, 128, 128)).save(dup)

        check = check_dataset(dataset)
        assert "画像数: 2" in check
        assert "caption未作成" in check
        assert "完全重複" in check

        caption_check = diagnose_captions(dataset, "eye", "日本語")
        assert "Caption診断" in caption_check
        assert "captionなし: 1" in caption_check
        assert "ノイズ語" in caption_check

        load_estimate = estimate_training_load(dataset, epochs=10, rank=16, resolution=512, lang="日本語")
        assert "学習負荷" in load_estimate
        assert "画像数: 2" in load_estimate

        rows = load_caption_rows(dataset)
        rows = remove_words_caption_rows(rows, "hair, background")
        rows = bulk_replace_caption_rows(rows, "blue", "green")
        saved = save_caption_rows(dataset, rows)
        assert "保存完了" in saved
        assert "green eyes" in img.with_suffix(".txt").read_text(encoding="utf-8")

        dataset_toml = Path(build_dataset_toml(dataset, output, 512))
        assert dataset_toml.exists()

        review = training_review(dataset, "eye", 16, 16, 10, 0.00005, 512, str(dataset_toml), "z-image", "日本語")
        assert "学習前レビュー" in review
        assert "Rank / Alpha: 16 / 16" in review

        project_path = output / "project.toml"
        pdata = project_data(str(dataset), str(output), str(dataset_toml), "z-image", "z-image", 16, 16, 10, 0.00005, "eye_lora_zimage", 512)
        assert "Saved project" in save_project(project_path, pdata)
        loaded = load_project(project_path)
        assert loaded["target_model"] == "z-image"
        assert int(loaded["rank"]) == 16

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
        assert "モデルアダプタ" in preview
        assert "cd " in preview
        assert "zimage_cache_latents.py" in preview
        assert "zimage_train_network.py" in preview
        wan_preview = preview_from_settings(
            settings_path=settings,
            dataset_toml=str(dataset_toml),
            target_model="wan2.2",
            rank=16,
            alpha=16,
            epochs=1,
            lr=0.00005,
            output_name="smoke_wan",
            task="t2v-A14B",
        )
        # wan2.2 is wired now: the legacy alias resolves to Wan2.2 T2V-A14B and builds a
        # real command set instead of reporting "not supported".
        assert "Wan2.2 T2V-A14B" in wan_preview
        assert "wan_cache_latents.py" in wan_preview
        assert "wan_train_network.py" in wan_preview
        assert "--dit_high_noise" in wan_preview

        missing_preflight = run_preflight(settings, str(dataset_toml), "z-image", "z-image")
        assert "モデルアダプタ" in missing_preflight
        assert "not found" in missing_preflight
        assert "Result: ❌" in missing_preflight

        valid_settings = root / "valid_settings.toml"
        write_existing_path_settings(valid_settings, musubi_repo, root / "models" / "z-image")
        ok_preflight = run_preflight(valid_settings, str(dataset_toml), "z-image", "z-image")
        assert "Result: ✅" in ok_preflight
        assert "zimage_dit" in ok_preflight

    print("Smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
