from __future__ import annotations

from pathlib import Path

import toml

from path_resolver import resolve_path


def build_dataset_toml(dataset_dir: Path, output_dir: Path, resolution: int) -> str:
    resolved_dataset_dir = resolve_path(dataset_dir)
    resolved_output_dir = resolve_path(output_dir)
    if not resolved_dataset_dir.exists():
        raise FileNotFoundError(f"Dataset folder not found: {resolved_dataset_dir}")

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = resolved_output_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    toml_path = resolved_output_dir / "dataset.toml"

    data = {
        "general": {
            "resolution": resolution,
            "caption_extension": ".txt",
        },
        "datasets": [
            {
                "image_directory": str(resolved_dataset_dir),
                "cache_directory": str(cache_dir),
                "num_repeats": 1,
            }
        ],
    }
    toml_path.write_text(toml.dumps(data), encoding="utf-8")
    return str(toml_path)
