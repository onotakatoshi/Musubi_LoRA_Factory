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
from error_analyzer import analyze_log, has_failure
from i18n import normalize_language, tr
from model_adapters import ADAPTERS, CatalogAdapter, adapter_ids, get_adapter
from model_registry import ALIASES, PROFILES, enabled_profiles, get_profile, normalize_profile_id, profile_ids, profile_summary
from model_settings_catalog import MODEL_SETTINGS
from model_ui import WIRED_PROFILE_IDS, available_model_ids
from pipeline import build_dataset_toml, check_dataset, export_file_name
from settings_detect import detect_model_files
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
    # Krea 2 trains on the RAW DiT and reuses the Qwen-Image VAE.
    assert get_adapter("krea2").validate_model_paths({}) == [
        "model_paths.krea2_dit",
        "model_paths.krea2_vae",
        "model_paths.krea2_text_encoder",
    ]
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

    # A healthy log must not be reported as broken. The analyzer used to match bare
    # words like "accelerate" and "safetensors", which appear in every successful run.
    healthy = "\n".join([
        "Trying to import sageattention",
        "Failed to import sageattention",
        "INFO:musubi_tuner.dataset.cache_io:epoch is incremented. current_epoch: 1, epoch: 2",
        "cd /repo && /venv/bin/python -m accelerate.commands.launch src/musubi_tuner/minimax_h3_train_network.py --dataset_config /d/dataset.toml",
        "steps: 100%|##########| 336/336 [44:09<00:00,  7.89s/it, avr_loss=5.37]",
    ])
    assert not has_failure(healthy), "a healthy log must not look like a failure"
    healthy_report = analyze_log(healthy)
    assert "✅" in healthy_report, healthy_report
    assert "Possible causes" not in healthy_report, healthy_report
    assert "推定段階: Train" in healthy_report, healthy_report

    broken = "\n".join([
        "Traceback (most recent call last):",
        '  File "/repo/src/musubi_tuner/minimax_h3/model.py", line 814, in _assert_block_device',
        "RuntimeError: MiniMax-H3 block 0 parameter attn.qkv_proj.weight is on cpu, expected cuda after wait",
    ])
    assert has_failure(broken)
    broken_report = analyze_log(broken)
    assert "❌" in broken_report, broken_report
    assert "blocks_to_swap" in broken_report, broken_report

    index_json = "SafetensorError: Error while deserializing header: HeaderTooLarge"
    assert "-00001-of-0000N.safetensors" in analyze_log(index_json)

    # Copying into ComfyUI must be able to rename, and must not escape the target dir.
    assert export_file_name(Path("/a/lora.safetensors"), "") == "lora.safetensors"
    assert export_file_name(Path("/a/lora.safetensors"), "marmot_v1") == "marmot_v1.safetensors"
    assert export_file_name(Path("/a/lora.safetensors"), "marmot_v1.safetensors") == "marmot_v1.safetensors"
    assert export_file_name(Path("/a/lora.safetensors"), "../../evil") == "evil.safetensors"

    # Detection must find the real files and must stay quiet rather than proposing
    # another model's weights when pointed somewhere without them.
    with tempfile.TemporaryDirectory() as detect_tmp:
        fake = Path(detect_tmp)
        zimage = fake / "z-image" / "Tongyi-MAI" / "Z-Image"
        for sub, names in [
            ("transformer", ["diffusion_pytorch_model-00001-of-00002.safetensors", "diffusion_pytorch_model-00002-of-00002.safetensors", "diffusion_pytorch_model.safetensors.index.json"]),
            ("vae", ["diffusion_pytorch_model.safetensors"]),
            ("text_encoder", ["model-00001-of-00003.safetensors", "model-00002-of-00003.safetensors"]),
        ]:
            (zimage / sub).mkdir(parents=True)
            for name in names:
                (zimage / sub / name).write_text("dummy", encoding="utf-8")

        detected = detect_model_files(zimage, "z-image")
        assert detected["zimage_dit"].endswith("diffusion_pytorch_model-00001-of-00002.safetensors"), detected
        assert detected["zimage_vae"].endswith("vae/diffusion_pytorch_model.safetensors"), detected
        assert detected["zimage_text_encoder"].endswith("model-00001-of-00003.safetensors"), detected
        assert not any(v.endswith(".index.json") for v in detected.values()), detected

        # A folder holding a different architecture must not be offered as Z-Image.
        other = fake / "elsewhere" / "diffusion_models"
        other.mkdir(parents=True)
        (other / "some_other_model_turbo_bf16.safetensors").write_text("dummy", encoding="utf-8")
        assert not any(detect_model_files(other.parent, "z-image").values()), "detection must not guess across models"

    # Krea 2's shift schedule must stay resolution-aware. A fixed
    # --discrete_flow_shift 2.5 is only correct at 1024x1024, so it must not be baked in.
    from commands import ModelPaths, build_krea2_preview
    krea2_preview = build_krea2_preview(
        musubi_python=Path("/venv/bin/python"), musubi_repo=Path("/repo"),
        dataset_toml=Path("/d/dataset.toml"), output_dir=Path("/d"), output_name="k",
        paths=ModelPaths(dit="/m/raw.safetensors", vae="/m/vae.safetensors", text_encoder="/m/te.safetensors"),
        rank=32, alpha=32, epochs=16, lr=1e-4,
    )
    assert "krea2_cache_latents.py" in krea2_preview
    assert "krea2_cache_text_encoder_outputs.py" in krea2_preview
    assert "networks.lora_krea2" in krea2_preview
    assert "--timestep_sampling krea2_shift" in krea2_preview, krea2_preview
    assert "--discrete_flow_shift" not in krea2_preview, "krea2_shift derives the shift per sample"

    print("Smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
