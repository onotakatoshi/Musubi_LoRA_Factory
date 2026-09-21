from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelPaths:
    vae: str = ""
    t5: str = ""
    dit: str = ""
    dit_high_noise: str = ""
    text_encoder: str = ""
    base_weights: str = ""
    video_vae: str = ""
    audio_vae: str = ""


def q(value: str | Path) -> str:
    return shlex.quote(str(value))


def in_repo(command: str, musubi_repo: Path) -> str:
    return f"cd {q(musubi_repo)} && {command}"


def accelerate_launch(musubi_python: Path, mixed_precision: str) -> list[str]:
    return [
        q(musubi_python),
        "-m",
        "accelerate.commands.launch",
        "--num_cpu_threads_per_process",
        "1",
        "--mixed_precision",
        mixed_precision,
    ]


def wan_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, i2v: bool = False) -> str:
    parts = [q(musubi_python), "src/musubi_tuner/wan_cache_latents.py", "--dataset_config", q(dataset_toml), "--vae", q(paths.vae)]
    if i2v:
        parts.append("--i2v")
    return in_repo(" ".join(parts), musubi_repo)


def wan_cache_text_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, batch_size: int = 16) -> str:
    command = " ".join([q(musubi_python), "src/musubi_tuner/wan_cache_text_encoder_outputs.py", "--dataset_config", q(dataset_toml), "--t5", q(paths.t5), "--batch_size", str(batch_size)])
    return in_repo(command, musubi_repo)


def wan_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    task: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    wan22_dual_dit: bool = True,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/wan_train_network.py", "--task", task, "--dit", q(paths.dit), "--dataset_config", q(dataset_toml),
        "--sdpa", "--mixed_precision", mixed_precision, "--optimizer_type", optimizer, "--learning_rate", str(lr),
        "--gradient_checkpointing", "--max_data_loader_n_workers", "2", "--persistent_data_loader_workers",
        "--network_module", "networks.lora_wan", "--network_dim", str(rank), "--network_alpha", str(alpha),
        "--timestep_sampling", "shift", "--max_train_epochs", str(epochs), "--save_every_n_epochs", "1", "--seed", "42",
        "--output_dir", q(output_dir), "--output_name", q(output_name),
    ]
    if task in {"t2v-A14B", "i2v-A14B"}:
        parts.extend(["--preserve_distribution_shape", "--force_v2_1_time_embedding"])
        parts.extend(["--discrete_flow_shift", "12.0" if task == "t2v-A14B" else "5.0"])
        if wan22_dual_dit and paths.dit_high_noise:
            parts.extend(["--dit_high_noise", q(paths.dit_high_noise), "--offload_inactive_dit"])
    else:
        parts.extend(["--discrete_flow_shift", "3.0", "--fp8_base"])
    return in_repo(" ".join(parts), musubi_repo)


def zimage_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths) -> str:
    command = " ".join([q(musubi_python), "src/musubi_tuner/zimage_cache_latents.py", "--dataset_config", q(dataset_toml), "--vae", q(paths.vae)])
    return in_repo(command, musubi_repo)


def zimage_cache_text_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, batch_size: int = 16, fp8_llm: bool = True) -> str:
    parts = [q(musubi_python), "src/musubi_tuner/zimage_cache_text_encoder_outputs.py", "--dataset_config", q(dataset_toml), "--text_encoder", q(paths.text_encoder), "--batch_size", str(batch_size)]
    if fp8_llm:
        parts.append("--fp8_llm")
    return in_repo(" ".join(parts), musubi_repo)


def zimage_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    fp8_base: bool = True,
    fp8_scaled: bool = True,
    fp8_llm: bool = True,
    blocks_to_swap: int = 0,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/zimage_train_network.py", "--dit", q(paths.dit), "--vae", q(paths.vae), "--text_encoder", q(paths.text_encoder),
        "--dataset_config", q(dataset_toml), "--sdpa", "--mixed_precision", mixed_precision, "--timestep_sampling", "shift",
        "--weighting_scheme", "none", "--discrete_flow_shift", "2.0", "--optimizer_type", optimizer, "--learning_rate", str(lr),
        "--gradient_checkpointing", "--max_data_loader_n_workers", "2", "--persistent_data_loader_workers",
        "--network_module", "networks.lora_z_image", "--network_dim", str(rank), "--network_alpha", str(alpha),
        "--max_train_epochs", str(epochs), "--save_every_n_epochs", "1", "--seed", "42",
        "--output_dir", q(output_dir), "--output_name", q(output_name),
    ]
    if fp8_base:
        parts.append("--fp8_base")
    if fp8_scaled:
        parts.append("--fp8_scaled")
    if fp8_llm:
        parts.append("--fp8_llm")
    if blocks_to_swap > 0:
        parts.extend(["--blocks_to_swap", str(blocks_to_swap)])
    if paths.base_weights:
        parts.extend(["--base_weights", q(paths.base_weights)])
    return in_repo(" ".join(parts), musubi_repo)


def build_zimage_preview(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, output_dir: Path, output_name: str, paths: ModelPaths, rank: int, alpha: int, epochs: int, lr: float) -> str:
    return "\n".join([
        "# 1. Latent cache",
        zimage_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 2. Text encoder cache",
        zimage_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        zimage_train_command(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, paths=paths, output_dir=output_dir, output_name=output_name, rank=rank, alpha=alpha, epochs=epochs, lr=lr),
    ])


def qwen_image_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths) -> str:
    command = " ".join([q(musubi_python), "src/musubi_tuner/qwen_image_cache_latents.py", "--dataset_config", q(dataset_toml), "--vae", q(paths.vae)])
    return in_repo(command, musubi_repo)


def qwen_image_cache_text_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, batch_size: int = 16, fp8_vl: bool = True) -> str:
    parts = [q(musubi_python), "src/musubi_tuner/qwen_image_cache_text_encoder_outputs.py", "--dataset_config", q(dataset_toml), "--text_encoder", q(paths.text_encoder), "--batch_size", str(batch_size)]
    if fp8_vl:
        parts.append("--fp8_vl")
    return in_repo(" ".join(parts), musubi_repo)


def qwen_image_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    fp8_scaled: bool = True,
    fp8_vl: bool = True,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/qwen_image_train_network.py", "--dit", q(paths.dit), "--vae", q(paths.vae), "--text_encoder", q(paths.text_encoder),
        "--dataset_config", q(dataset_toml), "--sdpa", "--mixed_precision", mixed_precision, "--timestep_sampling", "shift",
        "--optimizer_type", optimizer, "--learning_rate", str(lr), "--gradient_checkpointing",
        "--max_data_loader_n_workers", "2", "--persistent_data_loader_workers",
        "--network_module", "networks.lora_qwen_image", "--network_dim", str(rank), "--network_alpha", str(alpha),
        "--max_train_epochs", str(epochs), "--save_every_n_epochs", "1", "--seed", "42",
        "--output_dir", q(output_dir), "--output_name", q(output_name),
    ]
    if fp8_scaled:
        parts.append("--fp8_scaled")
    if fp8_vl:
        parts.append("--fp8_vl")
    return in_repo(" ".join(parts), musubi_repo)


def build_qwen_image_preview(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, output_dir: Path, output_name: str, paths: ModelPaths, rank: int, alpha: int, epochs: int, lr: float) -> str:
    return "\n".join([
        "# 1. Latent cache",
        qwen_image_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 2. Text encoder cache",
        qwen_image_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        qwen_image_train_command(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, paths=paths, output_dir=output_dir, output_name=output_name, rank=rank, alpha=alpha, epochs=epochs, lr=lr),
    ])


def build_wan_preview(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, output_dir: Path, output_name: str, paths: ModelPaths, rank: int, alpha: int, epochs: int, lr: float, task: str) -> str:
    return "\n".join([
        "# 1. Latent cache",
        wan_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths, i2v=task.startswith("i2v")),
        "",
        "# 2. Text encoder cache",
        wan_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        wan_train_command(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, paths=paths, output_dir=output_dir, output_name=output_name, task=task, rank=rank, alpha=alpha, epochs=epochs, lr=lr),
    ])



def flux_kontext_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths) -> str:
    command = " ".join([
        q(musubi_python), "src/musubi_tuner/flux_kontext_cache_latents.py",
        "--dataset_config", q(dataset_toml),
        "--vae", q(paths.vae),
    ])
    return in_repo(command, musubi_repo)


def flux_kontext_cache_text_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    batch_size: int = 16,
    fp8_t5: bool = True,
) -> str:
    parts = [
        q(musubi_python), "src/musubi_tuner/flux_kontext_cache_text_encoder_outputs.py",
        "--dataset_config", q(dataset_toml),
        "--text_encoder1", q(paths.t5),
        "--text_encoder2", q(paths.text_encoder),
        "--batch_size", str(batch_size),
    ]
    if fp8_t5:
        parts.append("--fp8_t5")
    return in_repo(" ".join(parts), musubi_repo)


def flux_kontext_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    fp8_scaled: bool = True,
    fp8_t5: bool = True,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/flux_kontext_train_network.py",
        "--dit", q(paths.dit),
        "--vae", q(paths.vae),
        "--text_encoder1", q(paths.t5),
        "--text_encoder2", q(paths.text_encoder),
        "--dataset_config", q(dataset_toml),
        "--sdpa",
        "--mixed_precision", mixed_precision,
        "--timestep_sampling", "shift",
        "--optimizer_type", optimizer,
        "--learning_rate", str(lr),
        "--gradient_checkpointing",
        "--max_data_loader_n_workers", "2",
        "--persistent_data_loader_workers",
        "--network_module", "networks.lora_flux",
        "--network_dim", str(rank),
        "--network_alpha", str(alpha),
        "--max_train_epochs", str(epochs),
        "--save_every_n_epochs", "1",
        "--seed", "42",
        "--output_dir", q(output_dir),
        "--output_name", q(output_name),
    ]
    if fp8_scaled:
        parts.append("--fp8_scaled")
    if fp8_t5:
        parts.append("--fp8_t5")
    return in_repo(" ".join(parts), musubi_repo)


def build_flux_kontext_preview(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    output_dir: Path,
    output_name: str,
    paths: ModelPaths,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
) -> str:
    return "\n".join([
        "# 1. Latent cache",
        flux_kontext_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 2. Text encoder cache",
        flux_kontext_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        flux_kontext_train_command(
            musubi_python=musubi_python,
            musubi_repo=musubi_repo,
            dataset_toml=dataset_toml,
            paths=paths,
            output_dir=output_dir,
            output_name=output_name,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
        ),
    ])


FLUX2_MODEL_VERSIONS = {
    "flux2-dev": "dev",
    "flux2-klein": "klein-9b",
}


def flux2_model_version(target_model: str) -> str:
    return FLUX2_MODEL_VERSIONS.get(target_model, "dev")


def flux2_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, model_version: str = "dev") -> str:
    command = " ".join([
        q(musubi_python), "src/musubi_tuner/flux_2_cache_latents.py",
        "--dataset_config", q(dataset_toml),
        "--model_version", model_version,
        "--vae", q(paths.vae),
    ])
    return in_repo(command, musubi_repo)


def flux2_cache_text_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    batch_size: int = 16,
    fp8_text_encoder: bool = True,
    model_version: str = "dev",
) -> str:
    parts = [
        q(musubi_python), "src/musubi_tuner/flux_2_cache_text_encoder_outputs.py",
        "--dataset_config", q(dataset_toml),
        "--model_version", model_version,
        "--text_encoder", q(paths.text_encoder),
        "--batch_size", str(batch_size),
    ]
    if fp8_text_encoder:
        parts.append("--fp8_text_encoder")
    return in_repo(" ".join(parts), musubi_repo)


def flux2_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    fp8_scaled: bool = True,
    fp8_text_encoder: bool = True,
    model_version: str = "dev",
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/flux_2_train_network.py",
        "--model_version", model_version,
        "--dit", q(paths.dit),
        "--vae", q(paths.vae),
        "--text_encoder", q(paths.text_encoder),
        "--dataset_config", q(dataset_toml),
        "--sdpa",
        "--mixed_precision", mixed_precision,
        "--timestep_sampling", "shift",
        "--optimizer_type", optimizer,
        "--learning_rate", str(lr),
        "--gradient_checkpointing",
        "--max_data_loader_n_workers", "2",
        "--persistent_data_loader_workers",
        "--network_module", "networks.lora_flux_2",
        "--network_dim", str(rank),
        "--network_alpha", str(alpha),
        "--max_train_epochs", str(epochs),
        "--save_every_n_epochs", "1",
        "--seed", "42",
        "--output_dir", q(output_dir),
        "--output_name", q(output_name),
    ]
    if fp8_scaled:
        parts.append("--fp8_scaled")
    if fp8_text_encoder:
        parts.append("--fp8_text_encoder")
    return in_repo(" ".join(parts), musubi_repo)


def build_flux2_preview(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    output_dir: Path,
    output_name: str,
    paths: ModelPaths,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    model_version: str = "dev",
) -> str:
    return "\n".join([
        "# 1. Latent cache",
        flux2_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths, model_version=model_version),
        "",
        "# 2. Text encoder cache",
        flux2_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths, model_version=model_version),
        "",
        "# 3. Train LoRA",
        flux2_train_command(
            musubi_python=musubi_python,
            musubi_repo=musubi_repo,
            dataset_toml=dataset_toml,
            paths=paths,
            output_dir=output_dir,
            output_name=output_name,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
            model_version=model_version,
        ),
    ])



def hunyuan_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths) -> str:
    command = " ".join([
        q(musubi_python), "src/musubi_tuner/cache_latents.py",
        "--dataset_config", q(dataset_toml),
        "--vae", q(paths.vae),
    ])
    return in_repo(command, musubi_repo)


def hunyuan_cache_text_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    batch_size: int = 16,
    fp8_llm: bool = True,
) -> str:
    parts = [
        q(musubi_python), "src/musubi_tuner/cache_text_encoder_outputs.py",
        "--dataset_config", q(dataset_toml),
        "--text_encoder1", q(paths.text_encoder),
        "--text_encoder2", q(paths.base_weights),
        "--batch_size", str(batch_size),
    ]
    if fp8_llm:
        parts.append("--fp8_llm")
    return in_repo(" ".join(parts), musubi_repo)


def hunyuan_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    fp8_base: bool = True,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/hv_train_network.py",
        "--dit", q(paths.dit),
        "--vae", q(paths.vae),
        "--text_encoder1", q(paths.text_encoder),
        "--text_encoder2", q(paths.base_weights),
        "--dataset_config", q(dataset_toml),
        "--sdpa",
        "--mixed_precision", mixed_precision,
        "--optimizer_type", optimizer,
        "--learning_rate", str(lr),
        "--gradient_checkpointing",
        "--max_data_loader_n_workers", "2",
        "--persistent_data_loader_workers",
        "--network_module", "networks.lora",
        "--network_dim", str(rank),
        "--network_alpha", str(alpha),
        "--timestep_sampling", "shift",
        "--discrete_flow_shift", "7.0",
        "--max_train_epochs", str(epochs),
        "--save_every_n_epochs", "1",
        "--seed", "42",
        "--output_dir", q(output_dir),
        "--output_name", q(output_name),
    ]
    if fp8_base:
        parts.append("--fp8_base")
    return in_repo(" ".join(parts), musubi_repo)


def build_hunyuan_preview(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    output_dir: Path,
    output_name: str,
    paths: ModelPaths,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
) -> str:
    return "\n".join([
        "# 1. Latent cache",
        hunyuan_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 2. Text encoder cache",
        hunyuan_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        hunyuan_train_command(
            musubi_python=musubi_python,
            musubi_repo=musubi_repo,
            dataset_toml=dataset_toml,
            paths=paths,
            output_dir=output_dir,
            output_name=output_name,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
        ),
    ])


# ---------------------------------------------------------------- MiniMax-H3

# H3 checkpoints are CFG-distilled, so musubi-tuner does not offer plain flow training.
# Of the three supported recipes we default to the guidance loss: it needs no
# third-party adapter file and works on the published BF16 base. When the user supplies
# a de-distillation adapter in minimax_h3_base_weights we switch to the training-adapter
# recipe instead, because the documentation says to pick exactly one.
MINIMAX_H3_TASKS = {"t2va", "fl2va", "ref2va"}
MINIMAX_H3_UNCOND_NAME = "h3_uncond.safetensors"


def minimax_h3_uncond_path(output_dir: Path) -> Path:
    return output_dir / MINIMAX_H3_UNCOND_NAME


def dataset_is_image_only(dataset_toml: Path) -> bool:
    """True when every dataset entry in the TOML is an image dataset.

    H3 treats images as an experimental one-frame mode: the plain image LoRA row of
    Table B needs --one_frame on all three steps and --video_only on training. This app
    builds image datasets, so that is the common case, but a hand-written TOML can point
    at videos instead.
    """
    try:
        import toml as _toml

        data = _toml.load(dataset_toml)
    except Exception:
        return False
    entries = data.get("datasets") or []
    if not entries:
        return False
    for entry in entries:
        if entry.get("video_directory") or entry.get("video_jsonl_file"):
            return False
    return True


def minimax_h3_cache_latents_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    task: str = "t2va",
    cache_seed: int = 42,
    one_frame: bool = False,
) -> str:
    parts = [
        q(musubi_python), "src/musubi_tuner/minimax_h3_cache_latents.py",
        "--dataset_config", q(dataset_toml),
        "--task", task,
        "--video_vae", q(paths.video_vae),
        "--audio_vae", q(paths.audio_vae),
        "--cache_seed", str(cache_seed),
        "--skip_existing",
    ]
    if one_frame:
        parts.append("--one_frame")
    return in_repo(" ".join(parts), musubi_repo)


def minimax_h3_cache_text_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    task: str = "t2va",
    text_cache_dtype: str = "bf16",
    text_encoder_blocks_to_swap: int = 50,
    guidance_loss: bool = True,
    one_frame: bool = False,
) -> str:
    parts = [
        q(musubi_python), "src/musubi_tuner/minimax_h3_cache_text_encoder_outputs.py",
        "--dataset_config", q(dataset_toml),
        "--task", task,
        "--text_encoder", q(paths.text_encoder),
        "--text_cache_dtype", text_cache_dtype,
        "--skip_existing",
    ]
    if one_frame:
        parts.append("--one_frame")
    if text_encoder_blocks_to_swap > 0:
        parts.extend(["--text_encoder_blocks_to_swap", str(text_encoder_blocks_to_swap)])
    if guidance_loss:
        # Writes the ~10 KB unconditional probe the training step re-anchors against.
        parts.extend(["--uncond_output", q(minimax_h3_uncond_path(output_dir))])
    return in_repo(" ".join(parts), musubi_repo)


def minimax_h3_train_command(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    paths: ModelPaths,
    output_dir: Path,
    output_name: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    task: str = "t2va",
    mixed_precision: str = "bf16",
    optimizer: str = "adamw8bit",
    # Block swap trades speed for memory and is only worth it on a VRAM-limited GPU. On
    # PGX (GB10, 128GB unified memory) the INT8 transformer fits without it. It is also
    # fragile at the top of its range: musubi-tuner accepts up to len(blocks)-2, but at
    # exactly that value block 0 was still on CPU when forward ran and training died with
    # "expected cuda after wait". Default to no swapping and let the caller opt in.
    blocks_to_swap: int = 0,
    guidance_loss_scale: float = 4.0,
    guidance_loss_sigma_min: float = 0.15,
    one_frame: bool = False,
) -> str:
    parts = [
        *accelerate_launch(musubi_python, mixed_precision),
        "src/musubi_tuner/minimax_h3_train_network.py",
        "--dataset_config", q(dataset_toml),
        "--task", task,
        "--dit", q(paths.dit),
        "--sdpa", "--mixed_precision", mixed_precision,
        # H3 derives its video and audio sigmas from one base time; these three are the
        # only values musubi-tuner accepts for this architecture.
        "--timestep_sampling", "uniform", "--weighting_scheme", "none", "--discrete_flow_shift", "1.0",
        "--optimizer_type", optimizer, "--learning_rate", str(lr),
        "--gradient_checkpointing", "--max_data_loader_n_workers", "2", "--persistent_data_loader_workers",
        "--network_module", "networks.lora_minimax_h3", "--network_dim", str(rank), "--network_alpha", str(alpha),
        "--max_train_epochs", str(epochs), "--save_every_n_epochs", "1", "--seed", "42",
        "--output_dir", q(output_dir), "--output_name", q(output_name),
    ]
    if one_frame:
        # --video_only drops the audio stream from the loss for single-frame image rows.
        parts.extend(["--one_frame", "--video_only"])
    if blocks_to_swap > 0:
        parts.extend(["--blocks_to_swap", str(blocks_to_swap)])
    if paths.base_weights:
        parts.extend(["--base_weights", q(paths.base_weights)])
    else:
        parts.extend([
            "--h3_guidance_loss_scale", str(guidance_loss_scale),
            "--h3_guidance_loss_sigma_min", str(guidance_loss_sigma_min),
            "--h3_guidance_loss_uncond_cache", q(minimax_h3_uncond_path(output_dir)),
        ])
    return in_repo(" ".join(parts), musubi_repo)


def build_minimax_h3_preview(
    musubi_python: Path,
    musubi_repo: Path,
    dataset_toml: Path,
    output_dir: Path,
    output_name: str,
    paths: ModelPaths,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    task: str = "t2va",
) -> str:
    guidance_loss = not paths.base_weights
    recipe = "training adapter (--base_weights)" if paths.base_weights else "guidance loss"
    one_frame = dataset_is_image_only(dataset_toml)
    mode = "one-frame image LoRA" if one_frame else "video"
    return "\n".join([
        f"# Recipe: {recipe}",
        f"# Dataset mode: {mode}",
        "",
        "# 1. Latent cache",
        minimax_h3_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths, task=task, one_frame=one_frame),
        "",
        "# 2. Text encoder cache",
        minimax_h3_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths, output_dir, task=task, guidance_loss=guidance_loss, one_frame=one_frame),
        "",
        "# 3. Train LoRA",
        minimax_h3_train_command(
            musubi_python=musubi_python,
            musubi_repo=musubi_repo,
            dataset_toml=dataset_toml,
            paths=paths,
            output_dir=output_dir,
            output_name=output_name,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
            task=task,
            one_frame=one_frame,
        ),
    ])


def build_command_preview(target_model: str, musubi_python: Path, musubi_repo: Path, dataset_toml: Path, output_dir: Path, output_name: str, paths: ModelPaths, rank: int, alpha: int, epochs: int, lr: float, task: str = "t2v-A14B") -> str:
    if target_model == "z-image":
        return build_zimage_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr)
    if target_model in {"wan2.2", "wan2.2-t2v-a14b", "wan2.2-i2v-a14b", "wan2.1"}:
        return build_wan_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr, task=task)
    if target_model == "qwen-image":
        return build_qwen_image_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr)
    if target_model == "flux-kontext":
        return build_flux_kontext_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr)
    if target_model in {"flux2-dev", "flux2-klein"}:
        return build_flux2_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr, model_version=flux2_model_version(target_model))
    if target_model == "minimax-h3":
        return build_minimax_h3_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr, task=task if task in MINIMAX_H3_TASKS else "t2va")
    if target_model == "hunyuan-video":
        return build_hunyuan_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr)
    return f"# {target_model} command template is not implemented yet."
