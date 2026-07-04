from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
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

from caption_diagnostics import diagnose_captions
from caption_table_widget import CaptionTableWidget
from command_preview import preview_from_settings
from env_check import check_environment
from error_analyzer import analyze_log
from export_validator import validate_lora_for_export
from gpu_monitor import gpu_preflight_warning
from i18n import SUPPORTED_LANGUAGES, normalize_language, tr
from image_caption_browser import ImageCaptionBrowser
from model_ui import available_model_labels, help_for_profile, label_for_profile, profile_id_from_label, task_for_profile, v1_default_profile
from output_detector import find_latest_lora, output_summary
from pipeline import AppConfig, build_dataset_toml, check_dataset, copy_lora_to_comfyui
from preflight import run_preflight
from project_io import default_project_path, load_project, project_data, save_project
from recommended_defaults import DEFAULTS, help_text as default_help_text, status_text as default_status_text
from settings_detect import detect_zimage_files, validate_settings_paths
from settings_io import load_settings, nested_get, save_settings
from state_check import config_status, dataset_status, train_ready_status
from step_guides import guide
from training_engine import TrainingEngine
from training_estimator import estimate_training_load
from training_presets import get_preset, preset_names, preset_summary
from training_review import training_review

SETTINGS_PATH = ROOT / "configs" / "settings.toml"

HELP = {
    "musubi_repo": "musubi-tunerをcloneしたフォルダです。src/musubi_tuner が中にある場所を指定します。",
    "musubi_python": "musubi-tuner用venvのpythonです。例: ../musubi-tuner/.venv/bin/python",
    "datasets_dir": "LoRA学習用データセットを置く親フォルダです。",
    "outputs_dir": "dataset.toml、cache、学習済みLoRAを置く親フォルダです。",
    "comfyui_loras_dir": "ComfyUIの models/loras フォルダです。Export時のコピー先です。",
    "zimage_dit": "Z-Imageの学習対象DiTです。初期はBaseまたはDe-Turbo系を想定します。",
    "zimage_vae": "Z-Image用VAEファイルです。例: ae.safetensors",
    "zimage_text_encoder": "Z-Image用Text Encoderです。",
    "zimage_base_weights": "任意設定です。必要な場合だけ指定します。",
    "dataset_folder": "学習用画像を入れたフォルダです。画像と同じ名前の .txt がcaptionです。",
    "lora_type": "何を学習したいかです。eyeなら目を学習する前提でcaptionを整理します。",
    "output_folder": "dataset.toml、cache、学習済みLoRAを置く出力フォルダです。",
    "dataset_toml": "Build dataset.tomlで作られるmusubi-tuner用設定ファイルです。",
    "target_model": "どのモデル向けLoRAを作るかです。Ver 1.0ではZ-Image / Z-Image-Turboのみ表示します。内部構造は将来のモデル追加に対応しています。",
    "task_profile": "選択したモデルプロファイルに対応するmusubi-tuner taskです。Ver 1.0では z-image 固定です。",
    "output_name": "保存されるLoRA名です。",
}


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
        self.resize(1240, 860)
        self.command_preview_text = ""
        self.training_engine = TrainingEngine()
        self.training_engine.log_received.connect(self._append_training_log)
        self.training_engine.state_changed.connect(self._set_training_state)
        self.training_engine.all_finished.connect(self._training_all_finished)
        self.settings = load_settings(SETTINGS_PATH)
        self.lang = normalize_language(nested_get(self.settings, "ui", "language", "日本語"))
        self._rebuild_ui()

    def t(self, key: str) -> str:
        return tr(self.lang, key)

    def _rebuild_ui(self) -> None:
        self.setWindowTitle(self.t("app_title"))
        tabs = QTabWidget()
        tabs.addTab(self._settings_tab(), self.t("tab_settings"))
        tabs.addTab(self._system_tab(), self.t("tab_system"))
        tabs.addTab(self._dataset_tab(), self.t("tab_dataset"))
        tabs.addTab(self._caption_tab(), self.t("tab_caption"))
        tabs.addTab(self._preview_tab(), self.t("tab_preview"))
        tabs.addTab(self._config_tab(), self.t("tab_config"))
        tabs.addTab(self._train_tab(), self.t("tab_train"))
        tabs.addTab(self._export_tab(), self.t("tab_export"))
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

    def _compact_form(self) -> QFormLayout:
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(6)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        return form

    def _browse_dir_row(self, edit: QLineEdit) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(edit)
        row.addWidget(self._button(self.t("browse"), lambda: self._pick_dir(edit)))
        return row

    def _browse_file_row(self, edit: QLineEdit) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(edit)
        row.addWidget(self._button(self.t("browse"), lambda: self._pick_file(edit)))
        return row

    def _default_spin_row(self, name: str, widget: QSpinBox | QDoubleSpinBox) -> QHBoxLayout:
        label = QLabel(default_status_text(name, widget.value(), self.lang))
        reset_text = "Reset" if self.lang == "English" else "デフォルトに戻す"
        reset = self._button(reset_text, lambda: self._reset_default(name, widget, label))
        widget.valueChanged.connect(lambda _value: label.setText(default_status_text(name, widget.value(), self.lang)))
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(widget)
        row.addWidget(label)
        row.addWidget(reset)
        return row

    def _reset_default(self, name: str, widget: QSpinBox | QDoubleSpinBox, label: QLabel) -> None:
        widget.setValue(DEFAULTS[name])
        label.setText(default_status_text(name, widget.value(), self.lang))

    def _pick_dir(self, target: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, self.t("select_folder"), target.text() or str(Path.home()))
        if path:
            target.setText(path)

    def _pick_file(self, target: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.t("select_file"), target.text() or str(Path.home()))
        if path:
            target.setText(path)

    def _settings_tab(self) -> QWidget:
        box = QVBoxLayout()
        box.setContentsMargins(8, 8, 8, 8)
        box.setSpacing(6)

        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setPlainText(self.t("settings_intro"))
        guide_box.setMaximumHeight(82)
        box.addWidget(guide_box, 0)

        controls = QWidget()
        controls_box = QVBoxLayout()
        controls_box.setContentsMargins(0, 0, 0, 0)
        controls_box.setSpacing(6)
        form = self._compact_form()
        self.set_language = QComboBox(); self.set_language.addItems(SUPPORTED_LANGUAGES); self.set_language.setCurrentText(self.lang)
        form.addRow(HelpLabel(self.t("language"), "UIの表示言語です。デフォルトは日本語です。"), self.set_language)
        self.set_musubi_repo = self._line(nested_get(self.settings, "musubi", "repo_path"))
        form.addRow(HelpLabel(self.t("label_musubi_repo"), HELP["musubi_repo"]), self._browse_dir_row(self.set_musubi_repo))
        self.set_musubi_python = self._line(nested_get(self.settings, "musubi", "python_path"))
        form.addRow(HelpLabel(self.t("label_musubi_python"), HELP["musubi_python"]), self._browse_file_row(self.set_musubi_python))
        self.set_datasets_dir = self._line(nested_get(self.settings, "paths", "datasets_dir"))
        form.addRow(HelpLabel(self.t("label_datasets_dir"), HELP["datasets_dir"]), self._browse_dir_row(self.set_datasets_dir))
        self.set_outputs_dir = self._line(nested_get(self.settings, "paths", "outputs_dir"))
        form.addRow(HelpLabel(self.t("label_outputs_dir"), HELP["outputs_dir"]), self._browse_dir_row(self.set_outputs_dir))
        self.set_comfyui_loras_dir = self._line(nested_get(self.settings, "paths", "comfyui_loras_dir"))
        form.addRow(HelpLabel(self.t("label_comfyui_loras_dir"), HELP["comfyui_loras_dir"]), self._browse_dir_row(self.set_comfyui_loras_dir))
        self.set_zimage_dit = self._line(nested_get(self.settings, "model_paths", "zimage_dit"))
        form.addRow(HelpLabel(self.t("label_zimage_dit"), HELP["zimage_dit"]), self._browse_file_row(self.set_zimage_dit))
        self.set_zimage_vae = self._line(nested_get(self.settings, "model_paths", "zimage_vae"))
        form.addRow(HelpLabel(self.t("label_zimage_vae"), HELP["zimage_vae"]), self._browse_file_row(self.set_zimage_vae))
        self.set_zimage_text_encoder = self._line(nested_get(self.settings, "model_paths", "zimage_text_encoder"))
        form.addRow(HelpLabel(self.t("label_zimage_text_encoder"), HELP["zimage_text_encoder"]), self._browse_file_row(self.set_zimage_text_encoder))
        self.set_zimage_base_weights = self._line(nested_get(self.settings, "model_paths", "zimage_base_weights"))
        form.addRow(HelpLabel(self.t("label_zimage_base_weights"), HELP["zimage_base_weights"]), self._browse_file_row(self.set_zimage_base_weights))
        controls_box.addLayout(form)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(self._button(self.t("validate_settings"), self._validate_settings))
        row.addWidget(self._button(self.t("detect_zimage_files"), self._detect_zimage_files))
        row.addWidget(self._button(self.t("save_settings"), self._save_settings))
        row.addWidget(self._button(self.t("reload_settings"), self._reload_settings_fields))
        row.addStretch()
        controls_box.addLayout(row)
        controls.setLayout(controls_box)
        box.addWidget(controls, 0)

        self.settings_log = self._log()
        self.settings_log.setMinimumHeight(260)
        box.addWidget(self.settings_log, 1)
        w = QWidget(); w.setLayout(box); return w

    def _system_tab(self) -> QWidget:
        box = QVBoxLayout()
        intro = QTextEdit(); intro.setReadOnly(True); intro.setPlainText(self.t("system_intro")); intro.setMaximumHeight(90); box.addWidget(intro)
        row = QHBoxLayout()
        row.addWidget(self._button(self.t("environment_check"), lambda: self.system_log.setPlainText(check_environment(SETTINGS_PATH))))
        row.addWidget(self._button(self.t("gpu_status"), lambda: self.system_log.setPlainText(gpu_preflight_warning())))
        row.addStretch(); box.addLayout(row)
        self.system_log = self._log(); box.addWidget(self.system_log)
        w = QWidget(); w.setLayout(box); return w

    def _dataset_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("dataset")); guide_box.setMaximumHeight(190); box.addWidget(guide_box)
        form = self._compact_form()
        self.dataset_dir = self._line(str(Path(nested_get(self.settings, "paths", "datasets_dir")) / "Eye_Blue_v1"))
        form.addRow(HelpLabel(self.t("label_dataset_folder"), HELP["dataset_folder"]), self._browse_dir_row(self.dataset_dir))
        self.lora_type = QComboBox(); self.lora_type.addItems(preset_names())
        form.addRow(HelpLabel(self.t("label_lora_type"), HELP["lora_type"]), self.lora_type)
        box.addLayout(form)
        buttons = QHBoxLayout()
        buttons.addWidget(self._button(self.t("check_dataset"), self._check_dataset))
        buttons.addWidget(self._button(self.t("diagnose_captions"), self._diagnose_captions))
        buttons.addWidget(self._button(self.t("check_current_step"), self._dataset_status))
        buttons.addStretch(); box.addLayout(buttons)
        self.dataset_log = self._log(); box.addWidget(self.dataset_log)
        w = QWidget(); w.setLayout(box); return w

    def _caption_tab(self) -> QWidget:
        return CaptionTableWidget(lambda: self.dataset_dir.text(), lambda: self.lang)

    def _preview_tab(self) -> QWidget:
        return ImageCaptionBrowser(lambda: self.dataset_dir.text(), lambda: self.lang)

    def _config_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("config")); guide_box.setMaximumHeight(160); box.addWidget(guide_box)
        form = self._compact_form()
        self.output_dir = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage"))
        form.addRow(HelpLabel(self.t("label_output_folder"), HELP["output_folder"]), self._browse_dir_row(self.output_dir))
        self.resolution = QSpinBox(); self.resolution.setRange(256, 2048); self.resolution.setSingleStep(64); self.resolution.setValue(DEFAULTS["resolution"])
        form.addRow(HelpLabel(self.t("label_resolution"), default_help_text("resolution", self.lang)), self._default_spin_row("resolution", self.resolution))
        self.dataset_toml = self._line("")
        form.addRow(HelpLabel(self.t("label_dataset_toml"), HELP["dataset_toml"]), self.dataset_toml)
        box.addLayout(form)
        buttons = QHBoxLayout()
        buttons.addWidget(self._button(self.t("build_dataset_toml"), self._build_dataset_toml))
        buttons.addWidget(self._button(self.t("check_current_step"), lambda: self.config_log.setPlainText(config_status(self.dataset_toml.text()))))
        buttons.addStretch(); box.addLayout(buttons)
        self.config_log = self._log(); box.addWidget(self.config_log)
        w = QWidget(); w.setLayout(box); return w

    def _train_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("train")); guide_box.setMaximumHeight(210); box.addWidget(guide_box)
        form = self._compact_form()
        default_profile = v1_default_profile()
        self.target_model = QComboBox(); self.target_model.addItems(available_model_labels()); self.target_model.setCurrentText(label_for_profile(default_profile.id)); self.target_model.currentTextChanged.connect(self._sync_profile_task)
        form.addRow(HelpLabel(self.t("label_target_model"), help_for_profile(default_profile.id, self.lang)), self.target_model)
        self.task = QLineEdit(default_profile.task); self.task.setReadOnly(True)
        form.addRow(HelpLabel(self.t("label_task_profile"), HELP["task_profile"]), self.task)
        self.preset = QComboBox(); self.preset.addItems(preset_names()); self.preset.setCurrentText(self.lora_type.currentText())
        form.addRow(HelpLabel("Preset", "用途別の推奨設定です。Ver 1.0ではZ-Image用プリセットです。"), self.preset)
        self.rank = QSpinBox(); self.rank.setRange(4, 128); self.rank.setSingleStep(4); self.rank.setValue(DEFAULTS["rank"])
        form.addRow(HelpLabel(self.t("label_rank"), default_help_text("rank", self.lang)), self._default_spin_row("rank", self.rank))
        self.alpha = QSpinBox(); self.alpha.setRange(4, 128); self.alpha.setSingleStep(4); self.alpha.setValue(DEFAULTS["alpha"])
        form.addRow(HelpLabel(self.t("label_alpha"), default_help_text("alpha", self.lang)), self._default_spin_row("alpha", self.alpha))
        self.epochs = QSpinBox(); self.epochs.setRange(1, 100); self.epochs.setValue(DEFAULTS["epochs"])
        form.addRow(HelpLabel(self.t("label_epochs"), default_help_text("epochs", self.lang)), self._default_spin_row("epochs", self.epochs))
        self.lr = QDoubleSpinBox(); self.lr.setDecimals(8); self.lr.setRange(0.000001, 0.01); self.lr.setSingleStep(0.00001); self.lr.setValue(DEFAULTS["lr"])
        form.addRow(HelpLabel(self.t("label_lr"), default_help_text("lr", self.lang)), self._default_spin_row("lr", self.lr))
        self.output_name = self._line("eye_lora_zimage")
        form.addRow(HelpLabel(self.t("label_output_name"), HELP["output_name"]), self.output_name)
        box.addLayout(form)
        project_row = QHBoxLayout()
        project_row.addWidget(self._button("Preset適用", self._apply_preset))
        project_row.addWidget(self._button("学習前レビュー", self._training_review))
        project_row.addWidget(self._button("Project保存", self._save_project))
        project_row.addWidget(self._button("Project読み込み", self._load_project))
        project_row.addStretch(); box.addLayout(project_row)
        row1 = QHBoxLayout()
        row1.addWidget(self._button(self.t("preflight_check"), self._preflight))
        row1.addWidget(self._button(self.t("preview_commands"), self._preview_commands))
        row1.addWidget(self._button(self.t("estimate_training_load"), self._estimate_training_load))
        row1.addWidget(self._button(self.t("check_current_step"), lambda: self.train_status.setPlainText(train_ready_status(self.command_preview_text))))
        row1.addStretch(); box.addLayout(row1)
        self.train_status = self._log(); self.train_status.setMaximumHeight(150); box.addWidget(self.train_status)
        self.command_preview = self._log(); self.command_preview.setMaximumHeight(180); box.addWidget(QLabel(self.t("command_preview"))); box.addWidget(self.command_preview)
        row2 = QHBoxLayout()
        row2.addWidget(self._button(self.t("run_latent_cache"), lambda: self._run_section("latent_cache")))
        row2.addWidget(self._button(self.t("run_text_cache"), lambda: self._run_section("text_cache")))
        row2.addWidget(self._button(self.t("run_train"), lambda: self._run_section("train")))
        row2.addWidget(self._button("全部実行", self._run_all_training))
        row2.addWidget(self._button(self.t("stop"), self._stop_process))
        row2.addWidget(self._button(self.t("analyze_log"), lambda: self.analysis_log.setPlainText(analyze_log(self.run_log.toPlainText()))))
        row2.addStretch(); box.addLayout(row2)
        self.run_log = self._log(); box.addWidget(QLabel(self.t("run_log"))); box.addWidget(self.run_log)
        self.analysis_log = self._log(); self.analysis_log.setMaximumHeight(140); box.addWidget(QLabel(self.t("error_analysis"))); box.addWidget(self.analysis_log)
        self._sync_profile_task()
        w = QWidget(); w.setLayout(box); return w

    def _export_tab(self) -> QWidget:
        box = QVBoxLayout()
        guide_box = QTextEdit(); guide_box.setReadOnly(True); guide_box.setPlainText(guide("export")); guide_box.setMaximumHeight(160); box.addWidget(guide_box)
        self.lora_path = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage" / "eye_lora_zimage.safetensors"))
        box.addLayout(self._browse_file_row(self.lora_path))
        row = QHBoxLayout()
        row.addWidget(self._button("コピー前チェック", self._validate_export))
        row.addWidget(self._button(self.t("copy_to_comfyui"), self._copy_lora))
        row.addStretch(); box.addLayout(row)
        self.export_log = self._log(); box.addWidget(self.export_log)
        w = QWidget(); w.setLayout(box); return w

    def _current_profile_id(self) -> str:
        if not hasattr(self, "target_model"):
            return v1_default_profile().id
        return profile_id_from_label(self.target_model.currentText())

    def _current_task(self) -> str:
        return task_for_profile(self._current_profile_id())

    def _sync_profile_task(self) -> None:
        if hasattr(self, "task"):
            self.task.setText(self._current_task())
        if hasattr(self, "train_status"):
            self.train_status.setPlainText(help_for_profile(self._current_profile_id(), self.lang))

    def _settings_values(self) -> dict[str, str]:
        return {
            "musubi_repo": self.set_musubi_repo.text(), "musubi_python": self.set_musubi_python.text(),
            "datasets_dir": self.set_datasets_dir.text(), "outputs_dir": self.set_outputs_dir.text(),
            "comfyui_loras_dir": self.set_comfyui_loras_dir.text(), "zimage_dit": self.set_zimage_dit.text(),
            "zimage_vae": self.set_zimage_vae.text(), "zimage_text_encoder": self.set_zimage_text_encoder.text(),
            "zimage_base_weights": self.set_zimage_base_weights.text(),
        }

    def _validate_settings(self) -> None:
        self.settings_log.setPlainText(validate_settings_paths(self._settings_values(), self._current_profile_id()))

    def _detect_zimage_files(self) -> None:
        model_dir = QFileDialog.getExistingDirectory(self, self.t("select_zimage_folder"), str(Path.home()))
        if not model_dir:
            return
        found = detect_zimage_files(Path(model_dir))
        if found.get("zimage_dit"):
            self.set_zimage_dit.setText(found["zimage_dit"])
        if found.get("zimage_vae"):
            self.set_zimage_vae.setText(found["zimage_vae"])
        if found.get("zimage_text_encoder"):
            self.set_zimage_text_encoder.setText(found["zimage_text_encoder"])
        self.settings_log.setPlainText(f"# {self.t('detected_zimage_files')}\n\nDiT: {found.get('zimage_dit') or self.t('not_found')}\nVAE: {found.get('zimage_vae') or self.t('not_found')}\nText Encoder: {found.get('zimage_text_encoder') or self.t('not_found')}\n\n{self.t('confirm_save_after_detect')}")

    def _settings_data_from_fields(self) -> dict:
        data = load_settings(SETTINGS_PATH)
        data.setdefault("ui", {})["language"] = self.set_language.currentText()
        data.setdefault("musubi", {})["repo_path"] = self.set_musubi_repo.text()
        data["musubi"]["python_path"] = self.set_musubi_python.text()
        data.setdefault("paths", {})["datasets_dir"] = self.set_datasets_dir.text()
        data["paths"]["outputs_dir"] = self.set_outputs_dir.text()
        data["paths"]["comfyui_loras_dir"] = self.set_comfyui_loras_dir.text()
        data.setdefault("model_paths", {})["zimage_dit"] = self.set_zimage_dit.text()
        data["model_paths"]["zimage_vae"] = self.set_zimage_vae.text()
        data["model_paths"]["zimage_text_encoder"] = self.set_zimage_text_encoder.text()
        data["model_paths"]["zimage_base_weights"] = self.set_zimage_base_weights.text()
        return data

    def _save_settings(self) -> None:
        try:
            data = self._settings_data_from_fields()
            save_settings(SETTINGS_PATH, data)
            self.settings = data
            self.lang = normalize_language(nested_get(data, "ui", "language", "日本語"))
            self._rebuild_ui()
            self.settings_log.setPlainText(f"{self.t('settings_saved')}: {SETTINGS_PATH}\n\n" + check_environment(SETTINGS_PATH))
        except Exception as exc:
            self.settings_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def _reload_settings_fields(self) -> None:
        self.settings = load_settings(SETTINGS_PATH)
        self.lang = normalize_language(nested_get(self.settings, "ui", "language", "日本語"))
        self._rebuild_ui()

    def _check_dataset(self) -> None:
        self.dataset_log.setPlainText(check_dataset(Path(self.dataset_dir.text()), self.lang))

    def _diagnose_captions(self) -> None:
        self.dataset_log.setPlainText(diagnose_captions(Path(self.dataset_dir.text()), self.lora_type.currentText(), self.lang))

    def _dataset_status(self) -> None:
        self.dataset_log.setPlainText(dataset_status(self.dataset_dir.text()))

    def _build_dataset_toml(self) -> None:
        try:
            path = build_dataset_toml(Path(self.dataset_dir.text()), Path(self.output_dir.text()), self.resolution.value())
            self.dataset_toml.setText(path)
            self.config_log.setPlainText(f"OK: {path}")
        except Exception as exc:
            self.config_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def _apply_preset(self) -> None:
        p = get_preset(self.preset.currentText())
        self.lora_type.setCurrentText(p.lora_type)
        self.rank.setValue(p.rank)
        self.alpha.setValue(p.alpha)
        self.epochs.setValue(p.epochs)
        self.lr.setValue(p.lr)
        self.resolution.setValue(p.resolution)
        self.output_name.setText(f"{p.name}_lora_zimage")
        self.train_status.setPlainText(preset_summary(p.name, self.lang))

    def _training_review(self) -> None:
        self.train_status.setPlainText(training_review(Path(self.dataset_dir.text()), self.lora_type.currentText(), self.rank.value(), self.alpha.value(), self.epochs.value(), self.lr.value(), self.resolution.value(), self.dataset_toml.text(), self._current_profile_id(), self.lang))

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save project", str(default_project_path(self.output_dir.text())), "TOML (*.toml)")
        if not path:
            return
        data = project_data(self.dataset_dir.text(), self.output_dir.text(), self.dataset_toml.text(), self._current_profile_id(), self._current_task(), self.rank.value(), self.alpha.value(), self.epochs.value(), self.lr.value(), self.output_name.text(), self.resolution.value())
        self.train_status.setPlainText(save_project(Path(path), data))

    def _load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load project", str(Path.home()), "TOML (*.toml)")
        if not path:
            return
        data = load_project(Path(path))
        self.dataset_dir.setText(str(data.get("dataset_dir", self.dataset_dir.text())))
        self.output_dir.setText(str(data.get("output_dir", self.output_dir.text())))
        self.dataset_toml.setText(str(data.get("dataset_toml", self.dataset_toml.text())))
        profile_id = str(data.get("target_model", self._current_profile_id()))
        self.target_model.setCurrentText(label_for_profile(profile_id))
        self.task.setText(task_for_profile(profile_id))
        self.rank.setValue(int(data.get("rank", self.rank.value())))
        self.alpha.setValue(int(data.get("alpha", self.alpha.value())))
        self.epochs.setValue(int(data.get("epochs", self.epochs.value())))
        self.lr.setValue(float(data.get("learning_rate", self.lr.value())))
        self.output_name.setText(str(data.get("output_name", self.output_name.text())))
        self.resolution.setValue(int(data.get("resolution", self.resolution.value())))
        self.train_status.setPlainText(f"Loaded project: {path}")

    def _preflight(self) -> None:
        self.train_status.setPlainText(run_preflight(SETTINGS_PATH, self.dataset_toml.text(), self._current_profile_id(), self._current_task()))

    def _estimate_training_load(self) -> None:
        self.train_status.setPlainText(estimate_training_load(Path(self.dataset_dir.text()), self.epochs.value(), self.rank.value(), self.resolution.value(), self.lang))

    def _preview_commands(self) -> None:
        text = preview_from_settings(SETTINGS_PATH, self.dataset_toml.text(), self._current_profile_id(), self.rank.value(), self.alpha.value(), self.epochs.value(), self.lr.value(), self.output_name.text(), self._current_task())
        self.command_preview_text = text
        self.command_preview.setPlainText(text)
        self.train_status.setPlainText(self.training_engine.prepare(text))

    def _run_section(self, section: str) -> None:
        result = self.training_engine.run_one(section)
        if result.startswith("NG:"):
            QMessageBox.warning(self, self.t("no_command"), result)
        else:
            self.train_status.setPlainText(result)

    def _run_all_training(self) -> None:
        result = self.training_engine.run_all()
        if result.startswith("NG:"):
            QMessageBox.warning(self, self.t("no_command"), result)
        else:
            self.train_status.setPlainText(result)

    def _append_training_log(self, text: str) -> None:
        if not hasattr(self, "run_log"):
            return
        self.run_log.moveCursor(QTextCursor.MoveOperation.End)
        self.run_log.insertPlainText(text)
        self.run_log.moveCursor(QTextCursor.MoveOperation.End)

    def _set_training_state(self, text: str) -> None:
        if hasattr(self, "train_status"):
            self.train_status.setPlainText(text)

    def _training_all_finished(self) -> None:
        latest = find_latest_lora(self.output_dir.text(), self.output_name.text()) if hasattr(self, "output_dir") else None
        if latest is not None and hasattr(self, "lora_path"):
            self.lora_path.setText(str(latest))
        message = "学習パイプラインが完了しました。\n\n" + output_summary(self.output_dir.text(), self.output_name.text())
        if latest is not None:
            message += "\n\n書き出しタブのLoRAパスへ自動セットしました。ComfyUIへコピーしてください。"
        else:
            message += "\n\nLoRAが自動検出できない場合は、出力フォルダから .safetensors を手動で選択してください。"
        if hasattr(self, "analysis_log"):
            self.analysis_log.setPlainText(message)
        if hasattr(self, "export_log"):
            self.export_log.setPlainText(message)

    def _stop_process(self) -> None:
        self.training_engine.stop()
        if hasattr(self, "run_log"):
            self.run_log.append(f"\n{self.t('stop_requested')}")

    def _validate_export(self) -> str:
        try:
            cfg = AppConfig.from_file(SETTINGS_PATH)
            report = validate_lora_for_export(self.lora_path.text(), cfg.comfyui_loras_dir)
        except Exception as exc:
            report = f"NG: {type(exc).__name__}: {exc}"
        self.export_log.setPlainText(report)
        return report

    def _copy_lora(self) -> None:
        try:
            report = self._validate_export()
            if "Result: OK" not in report:
                QMessageBox.warning(self, self.t("copy_to_comfyui"), report)
                return
            cfg = AppConfig.from_file(SETTINGS_PATH)
            self.export_log.setPlainText(report + "\n\n" + copy_lora_to_comfyui(Path(self.lora_path.text()), cfg))
        except Exception as exc:
            self.export_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")


def main() -> int:
    app = QApplication(sys.argv)
    win = DesktopApp()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
