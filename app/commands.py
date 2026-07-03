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


def q(value: str | Path) -> str:
    return shlex.quote(str(value))


def wan_cache_latents_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, i2v: bool = False) -> str:
    parts = [
        q(musubi_python),
        "src/musubi_tuner/wan_cache_latents.py",
        "--dataset_config", q(dataset_toml),
        "--vae", q(paths.vae),
    ]
    if i2v:
        parts.append("--i2v")
    return " ".join(parts)


def wan_cache_text_command(musubi_python: Path, musubi_repo: Path, dataset_toml: Path, paths: ModelPaths, batch_size: int = 16) -> str:
    return " ".join([
        q(musubi_python),
        "src/musubi_tuner/wan_cache_text_encoder_outputs.py",
        "--dataset_config", q(dataset_toml),
        "--t5", q(paths.t5),
        "--batch_size", str(batch_size),
    ])


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
        "accelerate", "launch",
        "--num_cpu_threads_per_process", "1",
        "--mixed_precision", mixed_precision,
        "src/musubi_tuner/wan_train_network.py",
        "--task", task,
        "--dit", q(paths.dit),
        "--dataset_config", q(dataset_toml),
        "--sdpa",
        "--mixed_precision", mixed_precision,
        "--optimizer_type", optimizer,
        "--learning_rate", str(lr),
        "--gradient_checkpointing",
        "--max_data_loader_n_workers", "2",
        "--persistent_data_loader_workers",
        "--network_module", "networks.lora_wan",
        "--network_dim", str(rank),
        "--network_alpha", str(alpha),
        "--timestep_sampling", "shift",
        "--max_train_epochs", str(epochs),
        "--save_every_n_epochs", "1",
        "--seed", "42",
        "--output_dir", q(output_dir),
        "--output_name", q(output_name),
    ]
    if task in {"t2v-A14B", "i2v-A14B"}:
        parts.extend(["--preserve_distribution_shape", "--force_v2_1_time_embedding"])
        if task == "t2v-A14B":
            parts.extend(["--discrete_flow_shift", "12.0"])
        else:
            parts.extend(["--discrete_flow_shift", "5.0"])
        if wan22_dual_dit and paths.dit_high_noise:
            parts.extend(["--dit_high_noise", q(paths.dit_high_noise), "--offload_inactive_dit"])
    else:
        parts.extend(["--discrete_flow_shift", "3.0", "--fp8_base"])
    return " ".join(parts)


def build_command_preview(
    target_model: str,
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
    task: str = "t2v-A14B",
) -> str:
    if target_model != "wan2.2":
        return (
            f"# {target_model} command template is not implemented yet.\n"
            "# Next target: add Z-Image / FLUX / HunyuanVideo profiles."
        )

    commands = [
        "# 1. Latent cache",
        wan_cache_latents_command(musubi_python, musubi_repo, dataset_toml, paths, i2v=task.startswith("i2v")),
        "",
        "# 2. Text encoder cache",
        wan_cache_text_command(musubi_python, musubi_repo, dataset_toml, paths),
        "",
        "# 3. Train LoRA",
        wan_train_command(
            musubi_repo=musubi_repo,
            dataset_toml=dataset_toml,
            paths=paths,
            output_dir=output_dir,
            output_name=output_name,
            task=task,
            rank=rank,
            alpha=alpha,
            epochs=epochs,
            lr=lr,
        ),
    ]
    return "\n".join(commands)
