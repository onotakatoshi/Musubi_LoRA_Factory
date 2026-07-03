from __future__ import annotations

from pathlib import Path
from typing import Any

import toml


def project_data(
    dataset_dir: str,
    output_dir: str,
    dataset_toml: str,
    target_model: str,
    task: str,
    rank: int,
    alpha: int,
    epochs: int,
    lr: float,
    output_name: str,
    resolution: int,
) -> dict[str, Any]:
    return {
        "project": {
            "dataset_dir": dataset_dir,
            "output_dir": output_dir,
            "dataset_toml": dataset_toml,
            "target_model": target_model,
            "task": task,
            "rank": rank,
            "alpha": alpha,
            "epochs": epochs,
            "learning_rate": lr,
            "output_name": output_name,
            "resolution": resolution,
        }
    }


def save_project(path: Path, data: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(toml.dumps(data), encoding="utf-8")
    return f"Saved project: {path}"


def load_project(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return toml.load(path).get("project", {})


def default_project_path(output_dir: str) -> Path:
    out = Path(output_dir) if output_dir else Path.home()
    return out / "musubi_lora_project.toml"
