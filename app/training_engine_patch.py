from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QProcessEnvironment


ROOT = Path(__file__).resolve().parents[1]
TRITON_CACHE_DIR = ROOT / ".cache" / "triton"


def normalize_stage_name(stage: str) -> str:
    key = str(stage).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "latent_cache": "latent_cache",
        "latentcache": "latent_cache",
        "latents_cache": "latent_cache",
        "latentscache": "latent_cache",
        "text_cache": "text_cache",
        "textcache": "text_cache",
        "text_encoder_cache": "text_cache",
        "textencodercache": "text_cache",
        "train": "train",
        "training": "train",
        "学習": "train",
        "学習実行": "train",
    }
    return aliases.get(key, key)


def command_not_ready_message() -> str:
    return "NG: コマンドが未生成です。実行前のコマンド準備に失敗しています。dataset.toml と設定を確認してください。"


def patched_process_environment(self) -> QProcessEnvironment:
    env = QProcessEnvironment.systemEnvironment()
    env.insert("PYTHONUNBUFFERED", "1")
    env.insert("PYTHONIOENCODING", "utf-8")
    TRITON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    env.insert("TRITON_CACHE_DIR", str(TRITON_CACHE_DIR))
    env.insert("XDG_CACHE_HOME", str(ROOT / ".cache"))
    return env


def patched_run_one(self, stage: str) -> str:
    stage = normalize_stage_name(stage)
    if self.is_running():
        return "NG: another training process is already running"
    if not self.sections:
        return command_not_ready_message()
    valid_stages = ["latent_cache", "text_cache", "train"]
    if stage not in valid_stages:
        return f"NG: unknown command section: {stage}"
    if not self.sections.get(stage, "").strip():
        return f"NG: command section not found: {stage}\n実行前のコマンド準備に失敗しています。dataset.toml と設定を確認してください。"
    guard = self._guard_before_run()
    if guard:
        return "NG: 実行前パス検証に失敗しました。\n" + guard
    self.queue = []
    self._start_stage(stage)
    return f"OK: started {stage}"


def patched_run_all(self) -> str:
    if self.is_running():
        return "NG: another training process is already running"
    required = ["latent_cache", "text_cache", "train"]
    if not self.sections:
        return command_not_ready_message()
    missing = [stage for stage in required if not self.sections.get(stage, "").strip()]
    if missing:
        return "NG: missing command sections: " + ", ".join(missing) + "\n実行前のコマンド準備に失敗しています。dataset.toml と設定を確認してください。"
    guard = self._guard_before_run()
    if guard:
        return "NG: 実行前パス検証に失敗しました。\n" + guard
    self.queue = required[1:]
    self._start_stage(required[0])
    return "OK: started full training pipeline"


def apply_training_engine_patch(training_engine_class) -> None:
    training_engine_class.run_one = patched_run_one
    training_engine_class.run_all = patched_run_all
    training_engine_class._process_environment = patched_process_environment
