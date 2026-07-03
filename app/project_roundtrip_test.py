from __future__ import annotations

import tempfile
from pathlib import Path

from project_io import load_project, project_data, save_project


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "project.toml"
        data = project_data(
            dataset_dir="/datasets/eye",
            output_dir="/outputs/eye",
            dataset_toml="/outputs/eye/dataset.toml",
            target_model="z-image",
            task="z-image",
            rank=16,
            alpha=16,
            epochs=10,
            lr=0.00005,
            output_name="eye_lora_zimage",
            resolution=512,
        )
        message = save_project(path, data)
        assert "Saved project" in message
        loaded = load_project(path)
        assert loaded["dataset_dir"] == "/datasets/eye"
        assert loaded["output_dir"] == "/outputs/eye"
        assert loaded["dataset_toml"] == "/outputs/eye/dataset.toml"
        assert loaded["target_model"] == "z-image"
        assert loaded["task"] == "z-image"
        assert int(loaded["rank"]) == 16
        assert int(loaded["alpha"]) == 16
        assert int(loaded["epochs"]) == 10
        assert float(loaded["learning_rate"]) == 0.00005
        assert loaded["output_name"] == "eye_lora_zimage"
        assert int(loaded["resolution"]) == 512
    print("Project roundtrip test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
