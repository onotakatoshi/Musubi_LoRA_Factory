from __future__ import annotations

from pathlib import Path

from runner import split_command_sections, validate_command_preview
from training_engine import StageStatus, TrainingStage, TrainingState, infer_log_dir_from_sections


VALID_PREVIEW = """
# 1. Latent cache
echo latent

# 2. Text encoder cache
echo text

# 3. Train LoRA
python -m accelerate.commands.launch src/musubi_tuner/zimage_train_network.py --output_dir /tmp/zimage_output --output_name eye_lora_zimage
""".strip()


def main() -> int:
    assert validate_command_preview(VALID_PREVIEW).startswith("OK:")
    sections = split_command_sections(VALID_PREVIEW)
    assert infer_log_dir_from_sections(sections) == Path("/tmp/zimage_output/logs")

    equals_preview = VALID_PREVIEW.replace("--output_dir /tmp/zimage_output", "--output_dir=/tmp/zimage_output")
    assert infer_log_dir_from_sections(split_command_sections(equals_preview)) == Path("/tmp/zimage_output/logs")

    state = TrainingState()
    assert state.statuses[TrainingStage.LATENT_CACHE.value] == StageStatus.PENDING
    state.mark_running(TrainingStage.LATENT_CACHE.value, Path("/tmp/zimage_output/logs/test.log"))
    assert state.current_stage == TrainingStage.LATENT_CACHE.value
    assert state.statuses[TrainingStage.LATENT_CACHE.value] == StageStatus.RUNNING
    assert "log:" in state.text()
    state.mark_done(TrainingStage.LATENT_CACHE.value)
    assert state.current_stage is None
    assert state.statuses[TrainingStage.LATENT_CACHE.value] == StageStatus.DONE
    state.mark_failed(TrainingStage.TRAIN.value, 1, "failed")
    assert state.statuses[TrainingStage.TRAIN.value] == StageStatus.FAILED
    assert "failed" in state.text()
    state.mark_stopped(TrainingStage.TEXT_CACHE.value)
    assert state.statuses[TrainingStage.TEXT_CACHE.value] == StageStatus.STOPPED

    print("Training engine test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
