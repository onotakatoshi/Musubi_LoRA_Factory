from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from commands import ModelPaths, build_command_preview
from model_registry import get_profile, normalize_profile_id, profile_ids
from model_settings_catalog import optional_keys, required_keys


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


class CatalogAdapter:
    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id

    def required_setting_keys(self) -> list[str]:
        return required_keys(self.profile_id)

    def optional_setting_keys(self) -> list[str]:
        return optional_keys(self.profile_id)

    def validate_model_paths(self, model_paths: dict) -> list[str]:
        missing: list[str] = []
        for key in self.required_setting_keys():
            if not model_paths.get(key):
                missing.append(f"model_paths.{key}")
        return missing

    def build_commands(self, context: CommandContext) -> str:
        profile = get_profile(self.profile_id)
        return (
            f"NG: {profile.display_name} はTarget modelとして追加済みですが、"
            "学習コマンドテンプレートは未検証です。"
            "Settingsの必要ファイル確認までは使えます。"
        )


class ZImageAdapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("z-image")

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


class Wan22A14BAdapter(CatalogAdapter):
    def __init__(self, profile_id: str, *, prefix: str) -> None:
        super().__init__(profile_id)
        self.prefix = prefix

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get(f"{self.prefix}_vae", ""),
            t5=model_paths.get(f"{self.prefix}_t5", ""),
            dit=model_paths.get(f"{self.prefix}_dit", ""),
            dit_high_noise=model_paths.get(f"{self.prefix}_dit_high_noise", ""),
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


class QwenImageAdapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("qwen-image")

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get("qwen_image_vae", ""),
            dit=model_paths.get("qwen_image_dit", ""),
            text_encoder=model_paths.get("qwen_image_text_encoder", ""),
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



class FluxKontextAdapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("flux-kontext")

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get("flux_kontext_vae", ""),
            dit=model_paths.get("flux_kontext_dit", ""),
            t5=model_paths.get("flux_kontext_t5", ""),
            text_encoder=model_paths.get("flux_kontext_clip_l", ""),
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


class Flux2Adapter(CatalogAdapter):
    def __init__(self, profile_id: str, *, prefix: str) -> None:
        super().__init__(profile_id)
        self.prefix = prefix

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get(f"{self.prefix}_vae", ""),
            dit=model_paths.get(f"{self.prefix}_dit", ""),
            text_encoder=model_paths.get(f"{self.prefix}_text_encoder", ""),
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



class HunyuanVideoAdapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("hunyuan-video")

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            vae=model_paths.get("hv_vae", ""),
            dit=model_paths.get("hv_dit", ""),
            text_encoder=model_paths.get("hv_text_encoder1", ""),
            base_weights=model_paths.get("hv_text_encoder2", ""),
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


class MiniMaxH3Adapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("minimax-h3")

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            dit=model_paths.get("minimax_h3_dit", ""),
            text_encoder=model_paths.get("minimax_h3_text_encoder", ""),
            video_vae=model_paths.get("minimax_h3_video_vae", ""),
            audio_vae=model_paths.get("minimax_h3_audio_vae", ""),
            base_weights=model_paths.get("minimax_h3_base_weights", ""),
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


ADAPTERS: dict[str, ModelAdapter] = {profile_id: CatalogAdapter(profile_id) for profile_id in profile_ids(include_future=True)}
ADAPTERS["z-image"] = ZImageAdapter()
ADAPTERS["wan2.2-t2v-a14b"] = Wan22A14BAdapter("wan2.2-t2v-a14b", prefix="wan")
ADAPTERS["wan2.2-i2v-a14b"] = Wan22A14BAdapter("wan2.2-i2v-a14b", prefix="wan22_i2v")
ADAPTERS["wan2.1"] = Wan22A14BAdapter("wan2.1", prefix="wan21")
ADAPTERS["qwen-image"] = QwenImageAdapter()


def get_adapter(profile_id: str) -> ModelAdapter:
    resolved_profile_id = normalize_profile_id(profile_id)
    if resolved_profile_id not in ADAPTERS:
        profile = get_profile(resolved_profile_id)
        raise NotImplementedError(f"{profile.display_name} adapter is not implemented yet")
    return ADAPTERS[resolved_profile_id]


def adapter_ids() -> list[str]:
    return list(ADAPTERS.keys())

ADAPTERS["flux-kontext"] = FluxKontextAdapter()
ADAPTERS["flux2-dev"] = Flux2Adapter("flux2-dev", prefix="flux2_dev")
ADAPTERS["flux2-klein"] = Flux2Adapter("flux2-klein", prefix="flux2_klein")

ADAPTERS["hunyuan-video"] = HunyuanVideoAdapter()
class Krea2Adapter(CatalogAdapter):
    def __init__(self) -> None:
        super().__init__("krea2")

    def _paths(self, model_paths: dict) -> ModelPaths:
        return ModelPaths(
            dit=model_paths.get("krea2_dit", ""),
            vae=model_paths.get("krea2_vae", ""),
            text_encoder=model_paths.get("krea2_text_encoder", ""),
            base_weights=model_paths.get("krea2_base_weights", ""),
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


ADAPTERS["minimax-h3"] = MiniMaxH3Adapter()
ADAPTERS["krea2"] = Krea2Adapter()
