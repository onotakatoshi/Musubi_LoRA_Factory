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


def q(value: str | Path) -> str:
    return shlex.quote(str(value))


def in_repo(command: str, musubi_repo: Path) -> str:
    return f"cd {q(musubi_repo)} && {command}"


def wan_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, i2v: bool = False) -> str:
    parts = [q(musubi_python), "src/musubi_tuner/wan_cache_latents.py", "--dataset_config", q(dataset_toml), "--vae", q(paths.vae)]
    if i2v:
        parts.append("--i2v")
    return in_repo(" ".join(parts), musubi_repo)


def wan_cache_text_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, batch_size: int = 16) -> str:
    command = " ".join([q(musubi_python), "src/musubi_tuner/wan_cache_text_encoder_outputs.py", "--dataset_config", q(dataset_toml), "--t5", q(paths.t5), "--batch_size", str(batch_size)])
    return in_repo(command, musubi_repo)


def wan_train_command(
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
        "accelerate", "launch", "--num_cpu_threads_per_process", "1", "--mixed_precision", mixed_precision,
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
        "accelerate", "launch", "--num_cpu_threads_per_process", "1", "--mixed_precision", mixed_precision,
        "src/musubi_tuner/zimage_train_network.py", "--dit", q(paths.dit), "--vae", q(paths.vae), "--text_encoder", q(paths.text_encoder),
        "--dataset_config", q(dataset_toml), "--sdpa", "--mixed_precision", mixed_precision, "--timestep_sampling", "shift",
        "--weighting_scheme", "none", "--discrete_flow_shift", "2.0", "--optimizer_type", optimizer, "--learning_rate", str(lr),
        "--gradient_checkpointing", "--max_data_loader_n_workers", "2", "--persistent_data_loader_workers",
        "--network_module", "networks.lora_zimage", "--network_dim", str(rank), "--network_alpha", str(alpha),
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
        zimage_train_command(musubi_repo=musubi_repo, dataset_toml=dataset_toml, paths=paths, output_dir=output_dir, output_name=output_name, rank=rank, alpha=alpha, epochs=epochs, lr=lr),
    ])


def build_command_preview(target_model: str, musubi_python: Path, musubi_repo: Path, dataset_toml: Path, output_dir: Path, output_name: str, paths: ModelPaths, rank: int, alpha: int, epochs: int, lr: float, task: str = "t2v-A14B") -> str:
    if target_model == "z-image":
        return build_zimage_preview(musubi_python=musubi_python, musubi_repo=musubi_repo, dataset_toml=dataset_toml, output_dir=output_dir, output_name=output_name, paths=paths, rank=rank, alpha=alpha, epochs=epochs, lr=lr)
    if target_model != "wan2.2":
        return f"# {target_model} command template is not implemented yet.\n# Next target: add FLUX / HunyuanVideo profiles."
    return "\n".join([
        "# 1. Latent cache",
        wan_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths, i2v=task.startswith("i2v")),
        "",
        "# 2. Text encoder cache",
        wan_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        wan_train_command(musubi_repo=musubi_repo, dataset_toml=dataset_toml, paths=paths, output_dir=output_dir, output_name=output_name, task=task, rank=rank, alpha=alpha, epochs=epochs, lr=lr),
    ])
