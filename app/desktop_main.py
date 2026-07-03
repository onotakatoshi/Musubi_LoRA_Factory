from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from command_preview import preview_from_settings
from env_check import check_environment
from error_analyzer import analyze_log
from gpu_monitor import gpu_preflight_warning
from pipeline import AppConfig, build_dataset_toml, check_dataset, copy_lora_to_comfyui
from preflight import run_preflight
from runner import split_command_sections
from settings_io import load_settings, nested_get, save_settings
from state_check import config_status, dataset_status, train_ready_status
from step_guides import guide

SETTINGS_PATH = ROOT / "configs" / "settings.toml"


class HelpLabel(QLabel):
    def __init__(self, text: str, help_text: str):
        super().__init__(text + "  ?")
        self.help_text = help_text
        self.setToolTip(help_text)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)

    def mousePressEvent(self, event):  # noqa: N802
        QMessageBox.information(self, self.text().replace("  ?", ""), self.help_text)


class DesktopApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Musubi LoRA Factory")
        self.resize(1240, 860)
        self.process: QProcess | None = None
        self.command_preview_text = ""
        self.settings = load_settings(SETTINGS_PATH)

        tabs = QTabWidget()
        tabs.addTab(self._settings_tab(), "Settings")
        tabs.addTab(self._system_tab(), "System")
        tabs.addTab(self._dataset_tab(), "1. Dataset")
        tabs.addTab(self._config_tab(), "2. Config")
        tabs.addTab(self._train_tab(), "3. Train")
        tabs.addTab(self._export_tab(), "4. Export")
        self.setCentralWidget(tabs)

    def _line(self, text: str = "") -> QLineEdit:
        w = QLineEdit()
        w.setText(text)
        return w

    def _log(self) -> QTextEdit:
        w = QTextEdit()
        w.setReadOnly(True)
        return w

    def _button(self, text: str, fn: Callable[[], None]) -> QPushButton:
        b = QPushButton(text)
        b.clicked.connect(fn)
        return b

    def _browse_dir_row(self, edit: QLineEdit) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(edit)
        row.addWidget(self._button("Browse", lambda: self._pick_dir(edit)))
        return row

    def _browse_file_row(self, edit: QLineEdit) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(edit)
        row.addWidget(self._button("Browse", lambda: self._pick_file(edit)))
        return row

    def _pick_dir(self, target: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select folder", target.text() or str(Path.home()))
        if path:
            target.setText(path)

    def _pick_file(self, target: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select file", target.text() or str(Path.home()))
        if path:
            target.setText(path)

    def _settings_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setPlainText(
            "Settings\n\n"
            "ここで musubi-tuner、Z-Imageモデル、ComfyUI、出力先のパスを設定します。\n"
            "保存すると configs/settings.toml に反映されます。通常はtomlを手で編集する必要はありません。"
        )
        guide_box.setMaximumHeight(120)
        box.addWidget(guide_box)

        form = QFormLayout()
        self.set_musubi_repo = self._line(nested_get(self.settings, "musubi", "repo_path"))
        form.addRow(HelpLabel("musubi-tuner repo", "musubi-tunerをcloneしたフォルダです。src/musubi_tuner が中にある場所を指定します。"), self._browse_dir_row(self.set_musubi_repo))
        self.set_musubi_python = self._line(nested_get(self.settings, "musubi", "python_path"))
        form.addRow(HelpLabel("musubi python", "musubi-tuner用venvのpythonです。例: /home/ono/musubi-tuner/.venv/bin/python"), self._browse_file_row(self.set_musubi_python))

        self.set_datasets_dir = self._line(nested_get(self.settings, "paths", "datasets_dir"))
        form.addRow(HelpLabel("datasets dir", "LoRA学習用データセットを置く親フォルダです。"), self._browse_dir_row(self.set_datasets_dir))
        self.set_outputs_dir = self._line(nested_get(self.settings, "paths", "outputs_dir"))
        form.addRow(HelpLabel("outputs dir", "dataset.toml、cache、学習済みLoRAを置く親フォルダです。"), self._browse_dir_row(self.set_outputs_dir))
        self.set_comfyui_loras_dir = self._line(nested_get(self.settings, "paths", "comfyui_loras_dir"))
        form.addRow(HelpLabel("ComfyUI loras dir", "ComfyUIの models/loras フォルダです。Export時のコピー先です。"), self._browse_dir_row(self.set_comfyui_loras_dir))

        self.set_zimage_dit = self._line(nested_get(self.settings, "model_paths", "zimage_dit"))
        form.addRow(HelpLabel("Z-Image DiT", "Z-Imageの学習対象DiTです。初期はBaseまたはDe-Turbo系を想定します。"), self._browse_file_row(self.set_zimage_dit))
        self.set_zimage_vae = self._line(nested_get(self.settings, "model_paths", "zimage_vae"))
        form.addRow(HelpLabel("Z-Image VAE", "Z-Image用VAEファイルです。例: ae.safetensors"), self._browse_file_row(self.set_zimage_vae))
        self.set_zimage_text_encoder = self._line(nested_get(self.settings, "model_paths", "zimage_text_encoder"))
        form.addRow(HelpLabel("Z-Image text encoder", "Z-Image用Text Encoderです。"), self._browse_file_row(self.set_zimage_text_encoder))
        self.set_zimage_base_weights = self._line(nested_get(self.settings, "model_paths", "zimage_base_weights"))
        form.addRow(HelpLabel("Z-Image base weights", "任意設定です。必要な場合だけ指定します。"), self._browse_file_row(self.set_zimage_base_weights))
        box.addLayout(form)

        row = QHBoxLayout()
        row.addWidget(self._button("Save Settings", self._save_settings))
        row.addWidget(self._button("Reload Settings", self._reload_settings_fields))
        row.addWidget(self._button("Environment Check", lambda: self.settings_log.setPlainText(check_environment(SETTINGS_PATH))))
        row.addStretch()
        box.addLayout(row)
        self.settings_log = self._log()
        self.settings_log.setMaximumHeight(180)
        box.addWidget(self.settings_log)
        w = QWidget(); w.setLayout(box); return w

    def _system_tab(self) -> QWidget:
        box = QVBoxLayout()
        intro = QTextEdit()
        intro.setReadOnly(True)
        intro.setPlainText(
            "Musubi LoRA Factory desktop app\n\n"
            "This is the initial musubi-tuner GUI.\n"
            "Use Settings first, then System -> Environment Check, then proceed from Dataset to Export."
        )
        intro.setMaximumHeight(100)
        box.addWidget(intro)
        row = QHBoxLayout()
        row.addWidget(self._button("Environment Check", lambda: self.system_log.setPlainText(check_environment(SETTINGS_PATH))))
        row.addWidget(self._button("GPU Status", lambda: self.system_log.setPlainText(gpu_preflight_warning())))
        row.addStretch()
        box.addLayout(row)
        self.system_log = self._log(); box.addWidget(self.system_log)
        w = QWidget(); w.setLayout(box); return w

    def _dataset_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("dataset")); guide_box.setMaximumHeight(190)
        box.addWidget(guide_box)
        form = QFormLayout()
        default_dataset = str(Path(nested_get(self.settings, "paths", "datasets_dir")) / "Eye_Blue_v1")
        self.dataset_dir = self._line(default_dataset)
        form.addRow(HelpLabel("Dataset folder", "学習用画像を入れたフォルダです。画像と同じ名前の .txt がcaptionです。"), self._browse_dir_row(self.dataset_dir))
        self.lora_type = QComboBox(); self.lora_type.addItems(["eye", "mouth", "face", "hair", "hand", "style", "clothing"])
        form.addRow(HelpLabel("LoRA type", "何を学習したいかです。eyeなら目を学習する前提でcaptionを整理します。"), self.lora_type)
        box.addLayout(form)
        buttons = QHBoxLayout()
        buttons.addWidget(self._button("Check Dataset", self._check_dataset))
        buttons.addWidget(self._button("Check Current Step", self._dataset_status))
        buttons.addStretch(); box.addLayout(buttons)
        self.dataset_log = self._log(); box.addWidget(self.dataset_log)
        w = QWidget(); w.setLayout(box); return w

    def _config_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("config")); guide_box.setMaximumHeight(160)
        box.addWidget(guide_box)
        form = QFormLayout()
        self.output_dir = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage"))
        form.addRow(HelpLabel("Output folder", "dataset.toml、cache、学習済みLoRAを置く出力フォルダです。"), self._browse_dir_row(self.output_dir))
        self.resolution = QSpinBox(); self.resolution.setRange(256, 2048); self.resolution.setSingleStep(64); self.resolution.setValue(512)
        form.addRow(HelpLabel("Resolution", "学習解像度です。最初は512推奨です。"), self.resolution)
        self.dataset_toml = self._line("")
        form.addRow(HelpLabel("dataset.toml", "Build dataset.tomlで作られるmusubi-tuner用設定ファイルです。"), self.dataset_toml)
        box.addLayout(form)
        buttons = QHBoxLayout()
        buttons.addWidget(self._button("Build dataset.toml", self._build_dataset_toml))
        buttons.addWidget(self._button("Check Current Step", lambda: self.config_log.setPlainText(config_status(self.dataset_toml.text()))))
        buttons.addStretch(); box.addLayout(buttons)
        self.config_log = self._log(); box.addWidget(self.config_log)
        w = QWidget(); w.setLayout(box); return w

    def _train_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("train")); guide_box.setMaximumHeight(210)
        box.addWidget(guide_box)
        form = QFormLayout()
        self.target_model = QComboBox(); self.target_model.addItems(["z-image", "wan2.2"])
        form.addRow(HelpLabel("Target model", "どのモデル向けLoRAを作るかです。初期版はz-image優先です。"), self.target_model)
        self.task = QComboBox(); self.task.addItems(["z-image", "t2v-A14B", "i2v-A14B", "t2v-1.3B"])
        form.addRow(HelpLabel("Task/profile", "Z-Imageではz-imageを選びます。Wan用項目は後続です。"), self.task)
        self.rank = QSpinBox(); self.rank.setRange(4, 128); self.rank.setSingleStep(4); self.rank.setValue(16)
        form.addRow(HelpLabel("Rank", "LoRAの表現力です。最初は16推奨です。"), self.rank)
        self.alpha = QSpinBox(); self.alpha.setRange(4, 128); self.alpha.setSingleStep(4); self.alpha.setValue(16)
        form.addRow(HelpLabel("Alpha", "LoRAの効きのスケールです。最初はRankと同じ値。"), self.alpha)
        self.epochs = QSpinBox(); self.epochs.setRange(1, 100); self.epochs.setValue(10)
        form.addRow(HelpLabel("Epochs", "データセットを何周学習するかです。最初は10程度。"), self.epochs)
        self.lr = QDoubleSpinBox(); self.lr.setDecimals(8); self.lr.setRange(0.000001, 0.01); self.lr.setValue(0.00005); self.lr.setSingleStep(0.00001)
        form.addRow(HelpLabel("Learning rate", "学習率です。最初は0.00005推奨です。"), self.lr)
        self.output_name = self._line("eye_lora_zimage")
        form.addRow(HelpLabel("Output name", "保存されるLoRA名です。"), self.output_name)
        box.addLayout(form)
        row1 = QHBoxLayout()
        row1.addWidget(self._button("0. Preflight Check", self._preflight))
        row1.addWidget(self._button("Preview Commands", self._preview_commands))
        row1.addWidget(self._button("Check Current Step", lambda: self.train_status.setPlainText(train_ready_status(self.command_preview_text))))
        row1.addStretch(); box.addLayout(row1)
        self.train_status = self._log(); self.train_status.setMaximumHeight(120); box.addWidget(self.train_status)
        self.command_preview = self._log(); self.command_preview.setMaximumHeight(180); box.addWidget(QLabel("Command Preview")); box.addWidget(self.command_preview)
        row2 = QHBoxLayout()
        row2.addWidget(self._button("Run 1: Latent Cache", lambda: self._run_section("latent_cache")))
        row2.addWidget(self._button("Run 2: Text Cache", lambda: self._run_section("text_cache")))
        row2.addWidget(self._button("Run 3: Train", lambda: self._run_section("train")))
        row2.addWidget(self._button("Stop", self._stop_process))
        row2.addWidget(self._button("Analyze Log", lambda: self.analysis_log.setPlainText(analyze_log(self.run_log.toPlainText()))))
        row2.addStretch(); box.addLayout(row2)
        self.run_log = self._log(); box.addWidget(QLabel("Run Log")); box.addWidget(self.run_log)
        self.analysis_log = self._log(); self.analysis_log.setMaximumHeight(140); box.addWidget(QLabel("Error Analysis")); box.addWidget(self.analysis_log)
        w = QWidget(); w.setLayout(box); return w

    def _export_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("export")); guide_box.setMaximumHeight(160)
        box.addWidget(guide_box)
        self.lora_path = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage" / "eye_lora_zimage.safetensors"))
        box.addLayout(self._browse_file_row(self.lora_path))
        box.addWidget(self._button("Copy to ComfyUI", self._copy_lora))
        self.export_log = self._log(); box.addWidget(self.export_log)
        w = QWidget(); w.setLayout(box); return w

    def _settings_data_from_fields(self) -> dict:
        data = load_settings(SETTINGS_PATH)
        data["musubi"]["repo_path"] = self.set_musubi_repo.text()
        data["musubi"]["python_path"] = self.set_musubi_python.text()
        data["paths"]["datasets_dir"] = self.set_datasets_dir.text()
        data["paths"]["outputs_dir"] = self.set_outputs_dir.text()
        data["paths"]["comfyui_loras_dir"] = self.set_comfyui_loras_dir.text()
        data["model_paths"]["zimage_dit"] = self.set_zimage_dit.text()
        data["model_paths"]["zimage_vae"] = self.set_zimage_vae.text()
        data["model_paths"]["zimage_text_encoder"] = self.set_zimage_text_encoder.text()
        data["model_paths"]["zimage_base_weights"] = self.set_zimage_base_weights.text()
        return data

    def _save_settings(self) -> None:
        try:
            data = self._settings_data_from_fields()
            save_settings(SETTINGS_PATH, data)
            self.settings = data
            self.settings_log.setPlainText(f"Saved: {SETTINGS_PATH}\n\n" + check_environment(SETTINGS_PATH))
        except Exception as exc:
            self.settings_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def _reload_settings_fields(self) -> None:
        self.settings = load_settings(SETTINGS_PATH)
        mapping = [
            (self.set_musubi_repo, "musubi", "repo_path"),
            (self.set_musubi_python, "musubi", "python_path"),
            (self.set_datasets_dir, "paths", "datasets_dir"),
            (self.set_outputs_dir, "paths", "outputs_dir"),
            (self.set_comfyui_loras_dir, "paths", "comfyui_loras_dir"),
            (self.set_zimage_dit, "model_paths", "zimage_dit"),
            (self.set_zimage_vae, "model_paths", "zimage_vae"),
            (self.set_zimage_text_encoder, "model_paths", "zimage_text_encoder"),
            (self.set_zimage_base_weights, "model_paths", "zimage_base_weights"),
        ]
        for widget, section, key in mapping:
            widget.setText(nested_get(self.settings, section, key))
        self.settings_log.setPlainText("Reloaded settings.")

    def _check_dataset(self) -> None:
        self.dataset_log.setPlainText(check_dataset(Path(self.dataset_dir.text())))

    def _dataset_status(self) -> None:
        self.dataset_log.setPlainText(dataset_status(self.dataset_dir.text()))

    def _build_dataset_toml(self) -> None:
        try:
            path = build_dataset_toml(Path(self.dataset_dir.text()), Path(self.output_dir.text()), self.resolution.value())
            self.dataset_toml.setText(path)
            self.config_log.setPlainText(f"OK: {path}")
        except Exception as exc:
            self.config_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def _preflight(self) -> None:
        self.train_status.setPlainText(run_preflight(SETTINGS_PATH, self.dataset_toml.text(), self.target_model.currentText(), self.task.currentText()))

    def _preview_commands(self) -> None:
        text = preview_from_settings(SETTINGS_PATH, self.dataset_toml.text(), self.target_model.currentText(), self.rank.value(), self.alpha.value(), self.epochs.value(), self.lr.value(), self.output_name.text(), self.task.currentText())
        self.command_preview_text = text
        self.command_preview.setPlainText(text)

    def _run_section(self, section: str) -> None:
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "Running", "A job is already running.")
            return
        sections = split_command_sections(self.command_preview_text)
        command = sections.get(section, "").strip()
        if not command:
            QMessageBox.warning(self, "No command", "Preview Commands first.")
            return
        self.run_log.clear()
        self.run_log.append(f"START: {command}\n")
        self.process = QProcess(self)
        self.process.setProgram("bash")
        self.process.setArguments(["-lc", command])
        self.process.readyReadStandardOutput.connect(self._read_process_output)
        self.process.readyReadStandardError.connect(self._read_process_output)
        self.process.finished.connect(lambda code, _status: self.run_log.append(f"\nDONE: exit code {code}" if code == 0 else f"\nFAILED: exit code {code}"))
        self.process.start()

    def _read_process_output(self) -> None:
        if not self.process:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
        err = bytes(self.process.readAllStandardError()).decode(errors="replace")
        if data:
            self.run_log.moveCursor(QTextCursor.MoveOperation.End)
            self.run_log.insertPlainText(data)
        if err:
            self.run_log.moveCursor(QTextCursor.MoveOperation.End)
            self.run_log.insertPlainText(err)

    def _stop_process(self) -> None:
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            self.run_log.append("\nSTOP requested")

    def _copy_lora(self) -> None:
        try:
            cfg = AppConfig.from_file(SETTINGS_PATH)
            self.export_log.setPlainText(copy_lora_to_comfyui(Path(self.lora_path.text()), cfg))
        except Exception as exc:
            self.export_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")


def main() -> int:
    app = QApplication(sys.argv)
    win = DesktopApp()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
