from __future__ import annotations

from pathlib import Path

import gradio as gr

from caption_editor import (
    bulk_replace_caption_rows,
    load_caption_rows,
    remove_words_caption_rows,
    save_caption_rows,
)
from command_preview import preview_from_settings
from env_check import check_environment
from error_analyzer import analyze_log
from gpu_monitor import gpu_preflight_warning
from help_text import HELP, help_markdown
from log_store import recent_logs_markdown
from pipeline import (
    AppConfig,
    build_dataset_toml,
    check_dataset,
    copy_lora_to_comfyui,
    generate_captions_placeholder,
    run_cache_placeholder,
    run_train_placeholder,
)
from preflight import run_preflight
from section_runner import stream_section
from state_check import config_status, dataset_status, train_ready_status
from step_guides import guide
from stream_runner import stop_job
from workflow import next_action, workflow_markdown

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "configs" / "settings.toml"


def load_config() -> AppConfig:
    return AppConfig.from_file(SETTINGS_PATH)


def ui_environment_check() -> str:
    return check_environment(SETTINGS_PATH)


def ui_gpu_status() -> str:
    return gpu_preflight_warning()


def ui_recent_logs() -> str:
    return recent_logs_markdown(ROOT)


def ui_help(topic: str) -> str:
    return help_markdown(topic)


def ui_dataset_status(dataset_dir: str) -> str:
    return dataset_status(dataset_dir)


def ui_config_status(dataset_toml: str) -> str:
    return config_status(dataset_toml)


def ui_train_ready_status(command_preview: str) -> str:
    return train_ready_status(command_preview)


def ui_check_dataset(dataset_dir: str) -> str:
    return check_dataset(Path(dataset_dir))


def ui_next_action(dataset_dir: str, dataset_toml: str = "", lora_path: str = "") -> str:
    return next_action(dataset_dir, dataset_toml, lora_path)


def ui_generate_captions(dataset_dir: str, lora_type: str, caption_mode: str) -> str:
    cfg = load_config()
    return generate_captions_placeholder(Path(dataset_dir), lora_type, caption_mode, cfg)


def ui_load_captions(dataset_dir: str) -> list[list[str]]:
    return load_caption_rows(Path(dataset_dir))


def ui_save_captions(dataset_dir: str, rows) -> str:
    return save_caption_rows(Path(dataset_dir), rows)


def ui_bulk_replace(rows, find_text: str, replace_text: str) -> list[list[str]]:
    return bulk_replace_caption_rows(rows, find_text, replace_text)


def ui_remove_words(rows, words_csv: str) -> list[list[str]]:
    return remove_words_caption_rows(rows, words_csv)


def ui_build_dataset_toml(dataset_dir: str, output_dir: str, resolution: int) -> str:
    try:
        return build_dataset_toml(Path(dataset_dir), Path(output_dir), resolution)
    except Exception as exc:
        return f"NG: {type(exc).__name__}: {exc}"


def ui_cache(dataset_toml: str, target_model: str) -> str:
    cfg = load_config()
    return run_cache_placeholder(Path(dataset_toml), target_model, cfg)


def ui_preflight(dataset_toml: str, target_model: str, task: str) -> str:
    return run_preflight(SETTINGS_PATH, dataset_toml, target_model, task)


def ui_command_preview(
    dataset_toml: str,
    target_model: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    output_name: str,
    task: str,
) -> str:
    return preview_from_settings(
        SETTINGS_PATH,
        dataset_toml,
        target_model,
        rank,
        alpha,
        epochs,
        lr,
        output_name,
        task,
    )


def ui_stream_command_section(command_preview: str, section: str):
    yield from stream_section(command_preview, section, cwd=ROOT)


def ui_stop(section: str) -> str:
    return stop_job(section)


def ui_analyze_log(log_text: str) -> str:
    return analyze_log(log_text)


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
    gr.Markdown("# Musubi LoRA Factory\nPGX向けmusubi-tuner GUI — Z-Image優先")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown(workflow_markdown(1))
        with gr.Column(scale=1):
            guide_dataset_dir = gr.Textbox(label="Dataset folder for guide", placeholder="/home/ono/datasets/lora/Eye_Blue_v1", info=HELP["dataset_dir"])
            guide_dataset_toml = gr.Textbox(label="dataset.toml for guide", placeholder="/home/ono/outputs/lora/Eye_Blue_v1_zimage/dataset.toml", info="Configタブで作成されるmusubi-tuner用データセット設定ファイルです。")
            guide_lora_path = gr.Textbox(label="LoRA path for guide", placeholder="/home/ono/outputs/lora/eye_lora_zimage.safetensors", info="学習後に生成されるLoRAファイルの場所です。")
            guide_btn = gr.Button("Show Next Action")
            guide_text = gr.Markdown("次にやること: Datasetフォルダを指定して、`Show Next Action` を押してください。")
            guide_btn.click(ui_next_action, inputs=[guide_dataset_dir, guide_dataset_toml, guide_lora_path], outputs=[guide_text])

    with gr.Accordion("Environment Check", open=False):
        env_btn = gr.Button("Run Environment Check")
        env_status = gr.Markdown("Z-Image用のmusubi-tuner環境とモデルパスを確認できます。")
        env_btn.click(ui_environment_check, outputs=[env_status])

    with gr.Accordion("? Help", open=False):
        help_topic = gr.Dropdown(["all"] + list(HELP.keys()), value="all", label="Help topic", info="知りたい項目を選ぶと説明が表示されます。")
        help_output = gr.Markdown(help_markdown("all"))
        help_topic.change(ui_help, inputs=[help_topic], outputs=[help_output])

    with gr.Accordion("GPU Status", open=False):
        gpu_btn = gr.Button("Refresh GPU Status")
        gpu_status = gr.Markdown("GPU status will appear here.")
        gpu_btn.click(ui_gpu_status, outputs=[gpu_status])

    with gr.Accordion("Recent Logs", open=False):
        logs_btn = gr.Button("Refresh Recent Logs")
        logs_status = gr.Markdown("Recent logs will appear here.")
        logs_btn.click(ui_recent_logs, outputs=[logs_status])

    with gr.Tab("1. Dataset"):
        with gr.Accordion("このステップで何をする？", open=True):
            gr.Markdown(guide("dataset"))
        dataset_dir = gr.Textbox(label="Dataset folder", placeholder="/home/ono/datasets/lora/Eye_Blue_v1", info=HELP["dataset_dir"])
        lora_type = gr.Dropdown(["eye", "mouth", "face", "hair", "hand", "style", "clothing"], value="eye", label="LoRA type", info=HELP["lora_type"])
        caption_mode = gr.Dropdown(["joycaption_llm", "joycaption_only", "llm_only", "manual"], value="joycaption_llm", label="Caption mode", info=HELP["caption_mode"])
        with gr.Row():
            check_btn = gr.Button("Check Dataset")
            dataset_status_btn = gr.Button("Check Current Step")
            caption_btn = gr.Button("Generate Captions")
        dataset_log = gr.Textbox(label="Log", lines=12, info="Check DatasetやGenerate Captionsの結果が表示されます。")
        check_btn.click(ui_check_dataset, inputs=[dataset_dir], outputs=[dataset_log])
        dataset_status_btn.click(ui_dataset_status, inputs=[dataset_dir], outputs=[dataset_log])
        caption_btn.click(ui_generate_captions, inputs=[dataset_dir, lora_type, caption_mode], outputs=[dataset_log])

    with gr.Tab("2. Caption Editor"):
        with gr.Accordion("このステップで何をする？", open=True):
            gr.Markdown(guide("caption"))
        load_caption_btn = gr.Button("Load Captions")
        caption_table = gr.Dataframe(headers=["image", "caption"], datatype=["str", "str"], interactive=True, label="Captions")
        with gr.Row():
            find_text = gr.Textbox(label="Find", placeholder="background", info="caption内で探す文字列です。")
            replace_text = gr.Textbox(label="Replace", placeholder="", info="置換後の文字列です。空にすると削除できます。")
        replace_btn = gr.Button("Bulk Replace")
        remove_words = gr.Textbox(label="Remove words CSV", placeholder="hair, clothes, background, woman, man", info="カンマ区切りで指定した語を含むタグを削除します。")
        remove_btn = gr.Button("Remove Words")
        save_caption_btn = gr.Button("Save Captions")
        caption_editor_log = gr.Textbox(label="Log", lines=4)
        load_caption_btn.click(ui_load_captions, inputs=[dataset_dir], outputs=[caption_table])
        replace_btn.click(ui_bulk_replace, inputs=[caption_table, find_text, replace_text], outputs=[caption_table])
        remove_btn.click(ui_remove_words, inputs=[caption_table, remove_words], outputs=[caption_table])
        save_caption_btn.click(ui_save_captions, inputs=[dataset_dir, caption_table], outputs=[caption_editor_log])

    with gr.Tab("3. Config"):
        with gr.Accordion("このステップで何をする？", open=True):
            gr.Markdown(guide("config"))
        output_dir = gr.Textbox(label="Output folder", placeholder="/home/ono/outputs/lora/Eye_Blue_v1_zimage", info=HELP["output_dir"])
        resolution = gr.Dropdown([512, 768, 1024], value=512, label="Resolution", info=HELP["resolution"])
        with gr.Row():
            build_btn = gr.Button("Build dataset.toml")
            config_status_btn = gr.Button("Check Current Step")
        dataset_toml = gr.Textbox(label="dataset.toml path", info="生成されたdataset.tomlのパスです。Trainタブで使います。")
        config_status_log = gr.Markdown("Config status will appear here.")
        build_btn.click(ui_build_dataset_toml, inputs=[dataset_dir, output_dir, resolution], outputs=[dataset_toml])
        config_status_btn.click(ui_config_status, inputs=[dataset_toml], outputs=[config_status_log])

    with gr.Tab("4. Train"):
        with gr.Accordion("このステップで何をする？", open=True):
            gr.Markdown(guide("train"))
        target_model = gr.Dropdown(["z-image", "wan2.2", "flux", "hunyuanvideo", "framepack"], value="z-image", label="Target model", info=HELP["target_model"])
        task = gr.Dropdown(["z-image", "t2v-A14B", "i2v-A14B", "t2v-1.3B"], value="z-image", label="Task/profile", info=HELP["task"])
        rank = gr.Slider(4, 128, value=16, step=4, label="Rank", info=HELP["rank"])
        alpha = gr.Slider(4, 128, value=16, step=4, label="Alpha", info=HELP["alpha"])
        epochs = gr.Slider(1, 50, value=10, step=1, label="Epochs", info=HELP["epochs"])
        lr = gr.Number(value=0.00005, label="Learning rate", info=HELP["lr"])
        output_name = gr.Textbox(value="eye_lora_zimage", label="Output name", info=HELP["output_name"])
        preflight_btn = gr.Button("0. Preflight Check")
        preflight_log = gr.Textbox(label="Preflight", lines=10, info=HELP["preflight"])
        with gr.Row():
            preview_btn = gr.Button("Preview Commands")
            train_status_btn = gr.Button("Check Current Step")
        command_preview = gr.Textbox(label="Command Preview", lines=16, info=HELP["preview"])
        train_status_log = gr.Markdown("Train status will appear here.")
        with gr.Row():
            run_latent_btn = gr.Button("Run 1: Latent Cache")
            run_text_btn = gr.Button("Run 2: Text Cache")
            run_train_btn = gr.Button("Run 3: Train")
            stop_btn = gr.Button("Stop Current Section")
            analyze_btn = gr.Button("Analyze Log")
        stop_section = gr.Dropdown(["latent_cache", "text_cache", "train"], value="train", label="Stop target", info="停止したい実行中セクションを選びます。通常はtrainです。")
        run_log = gr.Textbox(label="Run Log", lines=24, info="実行中のログです。長時間学習でもここに進行状況が流れます。")
        analysis_log = gr.Markdown("Error analysis will appear here.")
        preflight_btn.click(ui_preflight, inputs=[dataset_toml, target_model, task], outputs=[preflight_log])
        preview_btn.click(ui_command_preview, inputs=[dataset_toml, target_model, rank, alpha, epochs, lr, output_name, task], outputs=[command_preview])
        train_status_btn.click(ui_train_ready_status, inputs=[command_preview], outputs=[train_status_log])
        run_latent_btn.click(lambda text: ui_stream_command_section(text, "latent_cache"), inputs=[command_preview], outputs=[run_log])
        run_text_btn.click(lambda text: ui_stream_command_section(text, "text_cache"), inputs=[command_preview], outputs=[run_log])
        run_train_btn.click(lambda text: ui_stream_command_section(text, "train"), inputs=[command_preview], outputs=[run_log])
        stop_btn.click(ui_stop, inputs=[stop_section], outputs=[run_log])
        analyze_btn.click(ui_analyze_log, inputs=[run_log], outputs=[analysis_log])

    with gr.Tab("5. Export"):
        with gr.Accordion("このステップで何をする？", open=True):
            gr.Markdown(guide("export"))
        lora_path = gr.Textbox(label="LoRA file path", placeholder="/home/ono/outputs/lora/Eye_Blue_v1_zimage/eye_lora_zimage.safetensors", info="コピーしたいLoRAファイルのパスです。")
        copy_btn = gr.Button("Copy to ComfyUI")
        export_log = gr.Textbox(label="Log", lines=8, info=HELP["export"])
        copy_btn.click(ui_copy, inputs=[lora_path], outputs=[export_log])

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7865)
