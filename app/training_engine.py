from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QProcess, Signal

from runner import split_command_sections, validate_command_preview


class TrainingStage(str, Enum):
    LATENT_CACHE = "latent_cache"
    TEXT_CACHE = "text_cache"
    TRAIN = "train"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class TrainingState:
    statuses: dict[str, StageStatus] = field(default_factory=lambda: {
        TrainingStage.LATENT_CACHE.value: StageStatus.PENDING,
        TrainingStage.TEXT_CACHE.value: StageStatus.PENDING,
        TrainingStage.TRAIN.value: StageStatus.PENDING,
    })
    current_stage: str | None = None
    last_exit_code: int | None = None
    last_error: str = ""

    def mark_running(self, stage: str) -> None:
        self.current_stage = stage
        self.statuses[stage] = StageStatus.RUNNING
        self.last_error = ""

    def mark_done(self, stage: str) -> None:
        self.current_stage = None
        self.statuses[stage] = StageStatus.DONE
        self.last_exit_code = 0

    def mark_failed(self, stage: str, exit_code: int, error: str = "") -> None:
        self.current_stage = None
        self.statuses[stage] = StageStatus.FAILED
        self.last_exit_code = exit_code
        self.last_error = error

    def mark_stopped(self, stage: str) -> None:
        self.current_stage = None
        self.statuses[stage] = StageStatus.STOPPED
        self.last_error = "Stopped by user"

    def text(self) -> str:
        labels = {
            TrainingStage.LATENT_CACHE.value: "Latent Cache",
            TrainingStage.TEXT_CACHE.value: "Text Encoder Cache",
            TrainingStage.TRAIN.value: "Train",
        }
        icons = {
            StageStatus.PENDING: "□",
            StageStatus.RUNNING: "▶",
            StageStatus.DONE: "✓",
            StageStatus.FAILED: "×",
            StageStatus.STOPPED: "■",
        }
        lines = ["# Training State", ""]
        for key in [TrainingStage.LATENT_CACHE.value, TrainingStage.TEXT_CACHE.value, TrainingStage.TRAIN.value]:
            status = self.statuses[key]
            lines.append(f"{icons[status]} {labels[key]}: {status.value}")
        if self.last_exit_code is not None:
            lines.append(f"exit code: {self.last_exit_code}")
        if self.last_error:
            lines.append(f"last error: {self.last_error}")
        return "\n".join(lines)


class TrainingEngine(QObject):
    log_received = Signal(str)
    state_changed = Signal(str)
    stage_finished = Signal(str, int)
    all_finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.process: QProcess | None = None
        self.state = TrainingState()
        self.sections: dict[str, str] = {}
        self.queue: list[str] = []
        self._stop_requested = False

    def prepare(self, command_preview: str) -> str:
        validation = validate_command_preview(command_preview)
        if validation.startswith("NG:"):
            return validation
        self.sections = split_command_sections(command_preview)
        self.state = TrainingState()
        self.queue = []
        self._stop_requested = False
        self.state_changed.emit(self.state.text())
        return validation

    def run_one(self, stage: str) -> str:
        if self.is_running():
            return "NG: another training process is already running"
        if stage not in self.sections or not self.sections[stage].strip():
            return f"NG: command section not found: {stage}"
        self.queue = []
        self._start_stage(stage)
        return f"OK: started {stage}"

    def run_all(self) -> str:
        if self.is_running():
            return "NG: another training process is already running"
        required = [TrainingStage.LATENT_CACHE.value, TrainingStage.TEXT_CACHE.value, TrainingStage.TRAIN.value]
        missing = [stage for stage in required if not self.sections.get(stage, "").strip()]
        if missing:
            return "NG: missing command sections: " + ", ".join(missing)
        self.queue = required[1:]
        self._start_stage(required[0])
        return "OK: started full training pipeline"

    def stop(self) -> None:
        self._stop_requested = True
        self.queue = []
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()

    def is_running(self) -> bool:
        return self.process is not None and self.process.state() != QProcess.ProcessState.NotRunning

    def _start_stage(self, stage: str) -> None:
        command = self.sections[stage].strip()
        self.state.mark_running(stage)
        self.state_changed.emit(self.state.text())
        self.log_received.emit(f"\n===== START {stage} =====\n{command}\n")
        self.process = QProcess(self)
        self.process.setProgram("bash")
        self.process.setArguments(["-lc", command])
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_output)
        self.process.finished.connect(lambda code, _status, s=stage: self._on_finished(s, code))
        self.process.start()

    def _read_output(self) -> None:
        if not self.process:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        err = bytes(self.process.readAllStandardError()).decode(errors="replace")
        if data:
            self.log_received.emit(data)
        if err:
            self.log_received.emit(err)

    def _on_finished(self, stage: str, exit_code: int) -> None:
        if self._stop_requested:
            self.state.mark_stopped(stage)
            self.log_received.emit(f"\n===== STOPPED {stage} =====\n")
            self.state_changed.emit(self.state.text())
            self.stage_finished.emit(stage, exit_code)
            return
        if exit_code == 0:
            self.state.mark_done(stage)
            self.log_received.emit(f"\n===== DONE {stage} =====\n")
            self.state_changed.emit(self.state.text())
            self.stage_finished.emit(stage, exit_code)
            if self.queue:
                next_stage = self.queue.pop(0)
                self._start_stage(next_stage)
            else:
                self.all_finished.emit()
            return
        self.state.mark_failed(stage, exit_code, f"exit code {exit_code}")
        self.queue = []
        self.log_received.emit(f"\n===== FAILED {stage}: exit code {exit_code} =====\n")
        self.state_changed.emit(self.state.text())
        self.stage_finished.emit(stage, exit_code)
