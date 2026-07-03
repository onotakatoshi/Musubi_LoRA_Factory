from __future__ import annotations

from pathlib import Path

import gradio as gr

from pipeline import (
    AppConfig,
    build_dataset_toml,
    check_dataset,
    copy_lora_to_comfyui,
    generate_captions_placeholder,
    run_cache_placeholder,
    run_train_placeholder,
)

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"


def load_config() -> AppConfig:
    return AppConfig.from_file(SETTINGS_PATH)


def ui_check_dataset(dataset_dir: str) -> str:
    return check_dataset(Path(dataset_dir))


def ui_generate_captions(dataset_dir: str, lora_type: str, caption_mode: str) -> str:
    cfg = load_config()
    return generate_captions_placeholder(Path(dataset_dir), lora_type, caption_mode, cfg)


def ui_build_dataset_toml(dataset_dir: str, output_dir: str, resolution: int) -> str:
    return build_dataset_toml(Path(dataset_dir), Path(output_dir), resolution)


def ui_cache(dataset_toml: str, target_model: str) -> str:
    cfg = load_config()
    return run_cache_placeholder(Path(dataset_toml), target_model, cfg)


def ui_train(
    dataset_toml: str,
    target_model: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    output_name: str,
) -> str:
    cfg = load_config()
    return run_train_placeholder(Path(dataset_toml), target_model, rank, alpha, epochs, lr, output_name, cfg)


def ui_copy(lora_path: str) -> str:
    cfg = load_config()
    return copy_lora_to_comfyui(Path(lora_path), cfg)


with gr.Blocks(title="Musubi LoRA Factory") as demo:
    gr.Markdown("# Musubi LoRA Factory\nPGX向けLoRA作成MVP")

    with gr.Tab("1. Dataset"):
        dataset_dir = gr.Textbox(label="Dataset folder", placeholder="/home/ono/datasets/lora/Eye_Blue_v1")
        lora_type = gr.Dropdown(
            ["eye", "mouth", "face", "hair", "hand", "style", "clothing"],
            value="eye",
            label="LoRA type",
        )
        caption_mode = gr.Dropdown(
            ["joycaption_llm", "joycaption_only", "llm_only", "manual"],
            value="joycaption_llm",
            label="Caption mode",
        )
        check_btn = gr.Button("Check Dataset")
        caption_btn = gr.Button("Generate Captions")
        dataset_log = gr.Textbox(label="Log", lines=12)
        check_btn.click(ui_check_dataset, inputs=[dataset_dir], outputs=[dataset_log])
        caption_btn.click(ui_generate_captions, inputs=[dataset_dir, lora_type, caption_mode], outputs=[dataset_log])

    with gr.Tab("2. Config"):
        output_dir = gr.Textbox(label="Output folder", placeholder="/home/ono/outputs/lora/Eye_Blue_v1_wan22")
        resolution = gr.Dropdown([512, 768, 1024], value=512, label="Resolution")
        build_btn = gr.Button("Build dataset.toml")
        dataset_toml = gr.Textbox(label="dataset.toml path")
        build_btn.click(ui_build_dataset_toml, inputs=[dataset_dir, output_dir, resolution], outputs=[dataset_toml])

    with gr.Tab("3. Train"):
        target_model = gr.Dropdown(
            ["wan2.2", "z-image", "flux", "hunyuanvideo", "framepack"],
            value="wan2.2",
            label="Target model",
        )
        rank = gr.Slider(4, 128, value=16, step=4, label="Rank")
        alpha = gr.Slider(4, 128, value=16, step=4, label="Alpha")
        epochs = gr.Slider(1, 50, value=10, step=1, label="Epochs")
        lr = gr.Number(value=0.00005, label="Learning rate")
        output_name = gr.Textbox(value="eye_lora_wan22", label="Output name")
        cache_btn = gr.Button("Create Cache")
        train_btn = gr.Button("Train LoRA")
        train_log = gr.Textbox(label="Log", lines=16)
        cache_btn.click(ui_cache, inputs=[dataset_toml, target_model], outputs=[train_log])
        train_btn.click(ui_train, inputs=[dataset_toml, target_model, rank, alpha, epochs, lr, output_name], outputs=[train_log])

    with gr.Tab("4. Export"):
        lora_path = gr.Textbox(label="LoRA file path", placeholder="/home/ono/outputs/lora/eye_lora_wan22.safetensors")
        copy_btn = gr.Button("Copy to ComfyUI")
        export_log = gr.Textbox(label="Log", lines=8)
        copy_btn.click(ui_copy, inputs=[lora_path], outputs=[export_log])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7865)
