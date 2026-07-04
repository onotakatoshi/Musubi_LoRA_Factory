from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from model_ui import available_model_labels, label_for_profile, v1_default_profile
from recommended_defaults import DEFAULTS, REASONS_EN, REASONS_JA
from step_guides import guide
from training_presets import preset_names

SUCCESS_BUTTON_STYLE = """
QPushButton {
    background-color: #2f7d46;
    color: #ffffff;
    border: 1px solid #236236;
    border-radius: 5px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #286b3c;
}
QPushButton:pressed {
    background-color: #205530;
}
"""

DISPLAY_NAMES = {
    "rank": "Rank",
    "alpha": "Alpha",
    "epochs": "Epochs",
    "lr": "Learning rate",
}


def _group(title: str, layout: QVBoxLayout | QFormLayout | QHBoxLayout) -> QGroupBox:
    box = QGroupBox(title)
    box.setLayout(layout)
    return box


def _is_default_value(name: str, value: int | float) -> bool:
    default = DEFAULTS[name]
    if isinstance(default, float):
        return abs(float(value) - float(default)) < 1e-12
    return int(value) == int(default)


def _training_reason(name: str, lang: str) -> str:
    return (REASONS_EN if lang == "English" else REASONS_JA).get(name, "")


def _mark_button_success(button: QPushButton | None) -> None:
    if button is None:
        return
    text = button.text().replace(" ✓", "")
    button.setText(text + " ✓")
    button.setStyleSheet(SUCCESS_BUTTON_STYLE)


def _reset_button(button: QPushButton | None) -> None:
    if button is None:
        return
    button.setText(button.text().replace(" ✓", ""))
    button.setStyleSheet("")


def _training_param_row(self, name: str, widget: QSpinBox | QDoubleSpinBox) -> QHBoxLayout:
    title = QLabel(DISPLAY_NAMES[name])
    title.setMinimumWidth(105)
    status = QLabel()
    status.setMinimumWidth(94)
    default = DEFAULTS[name]
    reason = _training_reason(name, self.lang)
    detail = QLabel(f"デフォルト {default}　{reason}" if self.lang != "English" else f"Default {default}  {reason}")
    detail.setMinimumWidth(420)
    reset_text = "Reset" if self.lang == "English" else "デフォルトに戻す"
    reset = self._button(reset_text, lambda: widget.setValue(DEFAULTS[name]))

    def refresh() -> None:
        if _is_default_value(name, widget.value()):
            status.setText("推奨デフォルト" if self.lang != "English" else "Default")
        else:
            status.setText("ユーザー設定" if self.lang != "English" else "Custom")

    widget.valueChanged.connect(lambda _value: refresh())
    refresh()

    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    row.addWidget(title)
    row.addWidget(status)
    row.addWidget(widget)
    row.addWidget(detail, 1)
    row.addWidget(reset)
    return row


def _reset_execution_status_buttons(self) -> None:
    _reset_button(getattr(self, "btn_latent_cache", None))
    _reset_button(getattr(self, "btn_text_cache", None))
    _reset_button(getattr(self, "btn_train", None))


def _preflight_with_ui(self) -> None:
    self._preflight()
    text = self.train_status.toPlainText() if hasattr(self, "train_status") else ""
    if text and "NG:" not in text and ("OK" in text or "✓" in text or "✅" in text):
        _mark_button_success(getattr(self, "btn_preflight", None))


def _preview_commands_with_ui(self) -> None:
    self._preview_commands()
    text = self.train_status.toPlainText() if hasattr(self, "train_status") else ""
    preview = self.command_preview.toPlainText() if hasattr(self, "command_preview") else ""
    if text.startswith("OK:") or "3コマンドが揃っています" in text:
        _mark_button_success(getattr(self, "btn_command_preview", None))
        _reset_execution_status_buttons(self)
    elif "# 1. Latent cache" in preview and "# 2. Text encoder cache" in preview and "# 3. Train LoRA" in preview:
        _mark_button_success(getattr(self, "btn_command_preview", None))
        _reset_execution_status_buttons(self)


def _run_section_with_ui(self, section: str) -> None:
    self._run_section(section)


def _on_training_stage_finished_for_ui(self, stage: str, exit_code: int) -> None:
    if exit_code != 0:
        return
    if stage == "latent_cache":
        _mark_button_success(getattr(self, "btn_latent_cache", None))
    elif stage == "text_cache":
        _mark_button_success(getattr(self, "btn_text_cache", None))
    elif stage == "train":
        _mark_button_success(getattr(self, "btn_train", None))


def _connect_training_ui_signals(self) -> None:
    if getattr(self, "_training_ui_signals_connected", False):
        return
    self.training_engine.stage_finished.connect(self._on_training_stage_finished_for_ui)
    self._training_ui_signals_connected = True


def _train_tab(self) -> QWidget:
    page = QVBoxLayout()
    page.setContentsMargins(8, 8, 8, 8)
    page.setSpacing(8)
    _connect_training_ui_signals(self)

    guide_box = QTextEdit()
    guide_box.setReadOnly(True)
    guide_box.setPlainText(
        "操作順: 1) 事前チェック  2) コマンド確認  3) Latent Cache  4) Text Cache  5) 学習実行\n"
        "完了した操作はボタンが緑になります。緑になっていない工程は未完了または失敗です。\n\n"
        + guide("train")
    )
    guide_box.setMaximumHeight(120)
    page.addWidget(guide_box)

    default_profile = v1_default_profile()
    top_form = self._compact_form()
    self.target_model = QComboBox()
    self.target_model.addItems(available_model_labels())
    self.target_model.setCurrentText(label_for_profile(default_profile.id))
    self.target_model.currentTextChanged.connect(self._sync_profile_task)
    top_form.addRow("Target model", self.target_model)

    self.task = QLineEdit(default_profile.task)
    self.task.setReadOnly(True)
    top_form.addRow("Task", self.task)

    self.preset = QComboBox()
    self.preset.addItems(preset_names())
    if hasattr(self, "lora_type"):
        self.preset.setCurrentText(self.lora_type.currentText())
    top_form.addRow("Preset", self.preset)

    self.output_name = self._line("zimage_smoke_test")
    top_form.addRow("Output name", self.output_name)
    page.addWidget(_group("1. 基本設定", top_form))

    param_box = QVBoxLayout()
    param_box.setContentsMargins(8, 8, 8, 8)
    param_box.setSpacing(6)

    self.rank = QSpinBox()
    self.rank.setRange(4, 128)
    self.rank.setSingleStep(4)
    self.rank.setValue(DEFAULTS["rank"])
    param_box.addLayout(_training_param_row(self, "rank", self.rank))

    self.alpha = QSpinBox()
    self.alpha.setRange(4, 128)
    self.alpha.setSingleStep(4)
    self.alpha.setValue(DEFAULTS["alpha"])
    param_box.addLayout(_training_param_row(self, "alpha", self.alpha))

    self.epochs = QSpinBox()
    self.epochs.setRange(1, 100)
    self.epochs.setValue(DEFAULTS["epochs"])
    param_box.addLayout(_training_param_row(self, "epochs", self.epochs))

    self.lr = QDoubleSpinBox()
    self.lr.setDecimals(8)
    self.lr.setRange(0.000001, 0.01)
    self.lr.setSingleStep(0.00001)
    self.lr.setValue(DEFAULTS["lr"])
    param_box.addLayout(_training_param_row(self, "lr", self.lr))
    page.addWidget(_group("2. 学習パラメータ", param_box))

    prepare_row = QHBoxLayout()
    prepare_row.setSpacing(6)
    prepare_row.addWidget(self._button("Preset適用", self._apply_preset))
    prepare_row.addWidget(self._button("学習前レビュー", self._training_review))
    self.btn_preflight = self._button(self.t("preflight_check"), self._preflight_with_ui)
    self.btn_command_preview = self._button(self.t("preview_commands"), self._preview_commands_with_ui)
    prepare_row.addWidget(self.btn_preflight)
    prepare_row.addWidget(self.btn_command_preview)
    prepare_row.addWidget(self._button(self.t("estimate_training_load"), self._estimate_training_load))
    prepare_row.addStretch()
    page.addWidget(_group("3. 確認・準備", prepare_row))

    run_row = QHBoxLayout()
    run_row.setSpacing(6)
    self.btn_latent_cache = self._button("1. Latent Cache", lambda: self._run_section_with_ui("latent_cache"))
    self.btn_text_cache = self._button("2. Text Cache", lambda: self._run_section_with_ui("text_cache"))
    self.btn_train = self._button("3. 学習実行", lambda: self._run_section_with_ui("train"))
    run_row.addWidget(self.btn_latent_cache)
    run_row.addWidget(self.btn_text_cache)
    run_row.addWidget(self.btn_train)
    run_row.addWidget(self._button("全部実行", self._run_all_training))
    run_row.addWidget(self._button(self.t("stop"), self._stop_process))
    run_row.addWidget(self._button(self.t("analyze_log"), lambda: self.analysis_log.setPlainText(self._analyze_current_logs())))
    run_row.addStretch()
    page.addWidget(_group("4. 実行", run_row))

    project_row = QHBoxLayout()
    project_row.setSpacing(6)
    project_row.addWidget(self._button("Project保存", self._save_project))
    project_row.addWidget(self._button("Project読み込み", self._load_project))
    project_row.addStretch()
    page.addWidget(_group("Project", project_row))

    self.train_status = self._log()
    self.train_status.setMaximumHeight(115)
    page.addWidget(QLabel("状態"))
    page.addWidget(self.train_status)

    self.command_preview = self._log()
    self.command_preview.setMaximumHeight(145)
    page.addWidget(QLabel(self.t("command_preview")))
    page.addWidget(self.command_preview)

    self.run_log = self._log()
    page.addWidget(QLabel(self.t("run_log")))
    page.addWidget(self.run_log, 1)

    self.analysis_log = self._log()
    self.analysis_log.setMaximumHeight(145)
    page.addWidget(QLabel(self.t("error_analysis")))
    page.addWidget(self.analysis_log)

    self._sync_profile_task()
    w = QWidget()
    w.setLayout(page)
    return w


def _analyze_current_logs(self) -> str:
    from error_analyzer import analyze_log

    text = self.run_log.toPlainText() if hasattr(self, "run_log") else ""
    return analyze_log(text)


def apply_training_tab_patch(desktop_app_class) -> None:
    desktop_app_class._train_tab = _train_tab
    desktop_app_class._analyze_current_logs = _analyze_current_logs
    desktop_app_class._preflight_with_ui = _preflight_with_ui
    desktop_app_class._preview_commands_with_ui = _preview_commands_with_ui
    desktop_app_class._run_section_with_ui = _run_section_with_ui
    desktop_app_class._on_training_stage_finished_for_ui = _on_training_stage_finished_for_ui
