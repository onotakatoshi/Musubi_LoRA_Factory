from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

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
    started_at: float | None = None
    log_path: Path | None = None

    def mark_running(self, stage: str, log_path: Path | None = None) -> None:
        self.current_stage = stage
        self.statuses[stage] = StageStatus.RUNNING
        self.last_error = ""
        self.started_at = time.time()
        self.log_path = log_path

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

    def elapsed_text(self) -> str:
        if self.started_at is None:
            return ""
        elapsed = int(time.time() - self.started_at)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"elapsed: {hours}h {minutes}m {seconds}s"
        if minutes:
            return f"elapsed: {minutes}m {seconds}s"
        return f"elapsed: {seconds}s"

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
        elapsed = self.elapsed_text()
        if elapsed and self.current_stage:
            lines.append(elapsed)
        if self.log_path:
            lines.append(f"log: {self.log_path}")
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
        self._active_stage: str | None = None
        self._log_dir: Path | None = None
        self._log_file: Path | None = None
        self._ticker = QTimer(self)
        self._ticker.setInterval(1000)
        self._ticker.timeout.connect(self._tick)
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._force_kill)

    def prepare(self, command_preview: str, log_dir: str | Path | None = None) -> str:
        validation = validate_command_preview(command_preview)
        if validation.startswith("NG:"):
            return validation
        self.sections = split_command_sections(command_preview)
        self.state = TrainingState()
        self.queue = []
        self._stop_requested = False
        self._active_stage = None
        self._log_dir = Path(log_dir) if log_dir else None
        if self._log_dir:
            self._log_dir.mkdir(parents=True, exist_ok=True)
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
            self._emit_log("\n===== STOP REQUESTED =====\n")
            self.process.terminate()
            self._kill_timer.start(5000)

    def is_running(self) -> bool:
        return self.process is not None and self.process.state() != QProcess.ProcessState.NotRunning

    def _new_log_file(self, stage: str) -> Path | None:
        if not self._log_dir:
            return None
        stamp = time.strftime("%Y%m%d_%H%M%S")
        return self._log_dir / f"{stamp}_{stage}.log"

    def _emit_log(self, text: str) -> None:
        if self._log_file:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            with self._log_file.open("a", encoding="utf-8", errors="replace") as f:
                f.write(text)
        self.log_received.emit(text)

    def _start_stage(self, stage: str) -> None:
        command = self.sections[stage].strip()
        self._active_stage = stage
        self._log_file = self._new_log_file(stage)
        self.state.mark_running(stage, self._log_file)
        self.state_changed.emit(self.state.text())
        self._emit_log(f"\n===== START {stage} =====\n{command}\n")
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.setProgram("bash")
        self.process.setArguments(["-lc", command])
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_output)
        self.process.finished.connect(lambda code, _status, s=stage: self._on_finished(s, code))
        self.process.start()
        self._ticker.start()

    def _read_output(self) -> None:
        if not self.process:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        err = bytes(self.process.readAllStandardError()).decode(errors="replace")
        if data:
            self._emit_log(data)
        if err:
            self._emit_log(err)

    def _tick(self) -> None:
        if self.is_running():
            self.state_changed.emit(self.state.text())
        else:
            self._ticker.stop()

    def _force_kill(self) -> None:
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self._emit_log("\n===== FORCE KILL =====\n")
            self.process.kill()

    def _on_finished(self, stage: str, exit_code: int) -> None:
        self._ticker.stop()
        self._kill_timer.stop()
        self._read_output()
        if self._stop_requested:
            self.state.mark_stopped(stage)
            self._emit_log(f"\n===== STOPPED {stage} =====\n")
            self.state_changed.emit(self.state.text())
            self.stage_finished.emit(stage, exit_code)
            self._active_stage = None
            return
        if exit_code == 0:
            self.state.mark_done(stage)
            self._emit_log(f"\n===== DONE {stage} =====\n")
            self.state_changed.emit(self.state.text())
            self.stage_finished.emit(stage, exit_code)
            if self.queue:
                next_stage = self.queue.pop(0)
                self._start_stage(next_stage)
            else:
                self._active_stage = None
                self.all_finished.emit()
            return
        self.state.mark_failed(stage, exit_code, f"exit code {exit_code}")
        self.queue = []
        self._active_stage = None
        self._emit_log(f"\n===== FAILED {stage}: exit code {exit_code} =====\n")
        self.state_changed.emit(self.state.text())
        self.stage_finished.emit(stage, exit_code)
