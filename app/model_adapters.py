from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from commands import ModelPaths, build_command_preview
from model_registry import get_profile


@dataclass(frozen=True)
class CommandContext:
    musubi_python: Path
    musubi_repo: Path
    dataset_toml: Path
    output_dir: Path
    output_name: str
    model_paths: dict
    rank: int
    alpha: int
    epochs: int
    lr: float


class ModelAdapter(Protocol):
    profile_id: str

    def required_setting_keys(self) -> list[str]: ...
    def optional_setting_keys(self) -> list[str]: ...
    def validate_model_paths(self, model_paths: dict) -> list[str]: ...
    def build_commands(self, context: CommandContext) -> str: ...


class ZImageAdapter:
    profile_id = "z-image"

    def required_setting_keys(self) -> list[str]:
        return ["zimage_vae", "zimage_dit", "zimage_text_encoder"]

    def optional_setting_keys(self) -> list[str]:
        return ["zimage_base_weights"]

    def validate_model_paths(self, model_paths: dict) -> list[str]:
        missing: list[str] = []
        for key in self.required_setting_keys():
            if not model_paths.get(key):
                missing.append(f"model_paths.{key}")
        return missing

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get("zimage_vae", ""),
            dit=model_paths.get("zimage_dit", ""),
            text_encoder=model_paths.get("zimage_text_encoder", ""),
            base_weights=model_paths.get("zimage_base_weights", ""),
        )

    def build_commands(self, context: CommandContext) -> str:
        profile = get_profile(self.profile_id)
        return build_command_preview(
            target_model=profile.id,
            musubi_python=context.musubi_python,
            musubi_repo=context.musubi_repo,
            dataset_toml=context.dataset_toml,
            output_dir=context.output_dir,
            output_name=context.output_name,
            paths=self._paths(context.model_paths),
            rank=context.rank,
            alpha=context.alpha,
            epochs=context.epochs,
            lr=context.lr,
            task=profile.task,
        )


ADAPTERS: dict[str, ModelAdapter] = {
    "z-image": ZImageAdapter(),
}


def get_adapter(profile_id: str) -> ModelAdapter:
    if profile_id not in ADAPTERS:
        profile = get_profile(profile_id)
        raise NotImplementedError(f"{profile.display_name} adapter is not implemented yet")
    return ADAPTERS[profile_id]


def adapter_ids() -> list[str]:
    return list(ADAPTERS.keys())
