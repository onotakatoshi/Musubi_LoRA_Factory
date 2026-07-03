from __future__ import annotations

from training_engine import StageStatus, TrainingStage, TrainingState
from runner import validate_command_preview


VALID_PREVIEW = """
# 1. Latent cache
echo latent

# 2. Text encoder cache
echo text

# 3. Train LoRA
echo train
""".strip()


def main() -> int:
    assert validate_command_preview(VALID_PREVIEW).startswith("OK:")

    state = TrainingState()
    assert state.statuses[TrainingStage.LATENT_CACHE.value] == StageStatus.PENDING
    state.mark_running(TrainingStage.LATENT_CACHE.value)
    assert state.current_stage == TrainingStage.LATENT_CACHE.value
    assert state.statuses[TrainingStage.LATENT_CACHE.value] == StageStatus.RUNNING
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
