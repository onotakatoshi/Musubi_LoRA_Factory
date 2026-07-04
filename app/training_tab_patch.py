from __future__ import annotations

from PySide6.QtCore import Qt
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
from training_presets import preset_names

SUCCESS_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #16803f,
        stop:0.45 #0f6b35,
        stop:0.55 #0b542a,
        stop:1 #052e16);
    color: #f7fff9;
    border: 1px solid #4ade80;
    border-bottom: 2px solid #02140a;
    border-right: 2px solid #02140a;
    border-radius: 9px;
    padding: 7px 13px;
    font-weight: 900;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #22c55e,
        stop:0.45 #16803f,
        stop:0.55 #0f6b35,
        stop:1 #064e2c);
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #02140a,
        stop:1 #0f6b35);
    border-top: 2px solid #02140a;
    border-left: 2px solid #02140a;
    border-bottom: 1px solid #4ade80;
    border-right: 1px solid #4ade80;
    padding-top: 8px;
    padding-left: 14px;
}
"""

DISPLAY_NAMES = {
    "rank": "Rank",
    "alpha": "Alpha",
    "epochs": "Epochs",
    "lr": "Learning rate",
}


def _en(self) -> bool:
    return getattr(self, "lang", "日本語") == "English"


def _txt(self, ja: str, en: str) -> str:
    return en if _en(self) else ja


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
    title.setFixedWidth(96)
    title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    status = QLabel()
    status.setFixedWidth(72 if _en(self) else 54)

    widget.setFixedWidth(96)

    default = DEFAULTS[name]
    reason = _training_reason(name, self.lang)
    detail = QLabel(f"Default {default}  {reason}" if _en(self) else f"デフォルト {default}　{reason}")
    detail.setMinimumWidth(220)
    detail.setMaximumWidth(360)

    reset_text = "Reset" if _en(self) else "戻す"
    reset = self._button(reset_text, lambda: widget.setValue(DEFAULTS[name]))
    reset.setObjectName("resetButton")
    reset.setToolTip("Reset to default" if _en(self) else "デフォルトに戻す")
    reset.setFixedWidth(66 if _en(self) else 64)
    reset.setFixedHeight(28)

    def refresh() -> None:
        if _is_default_value(name, widget.value()):
            status.setText("Default" if _en(self) else "推奨")
        else:
            status.setText("Custom" if _en(self) else "変更")

    widget.valueChanged.connect(lambda _value: refresh())
    refresh()

    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    row.addWidget(title)
    row.addWidget(status)
    row.addWidget(widget)
    row.addWidget(detail)
    row.addWidget(reset)
    row.addStretch(1)
    return row


def _reset_execution_status_buttons(self) -> None:
    _reset_button(getattr(self, "btn_latent_cache", None))
    _reset_button(getattr(self, "btn_text_cache", None))
    _reset_button(getattr(self, "btn_train", None))


def _append_visible_log(self, text: str) -> None:
    if hasattr(self, "run_log"):
        self.run_log.append(text)


def _ensure_commands_ready(self) -> bool:
    preview_text = getattr(self, "command_preview_text", "")
    if preview_text and not preview_text.strip().startswith("NG:"):
        return True
    self._preview_commands()
    status = self.train_status.toPlainText() if hasattr(self, "train_status") else ""
    preview = self.command_preview.toPlainText() if hasattr(self, "command_preview") else ""
    if status.startswith("NG:") or preview.startswith("NG:"):
        _append_visible_log(self, "\n===== Command preparation failed =====\n" + (status or preview) if _en(self) else "\n===== 実行準備に失敗 =====\n" + (status or preview))
        return False
    if "# 1. Latent cache" in preview and "# 2. Text encoder cache" in preview and "# 3. Train LoRA" in preview:
        _append_visible_log(self, "\n===== Commands prepared automatically =====" if _en(self) else "\n===== コマンド自動準備 OK =====")
        _reset_execution_status_buttons(self)
        return True
    if status.startswith("OK:"):
        _append_visible_log(self, "\n===== Commands prepared automatically =====" if _en(self) else "\n===== コマンド自動準備 OK =====")
        _reset_execution_status_buttons(self)
        return True
    _append_visible_log(self, ("\n===== Check command preparation =====\n" if _en(self) else "\n===== 実行準備を確認してください =====\n") + status)
    return False


def _run_section_with_ui(self, section: str) -> None:
    if not _ensure_commands_ready(self):
        return
    self._run_section(section)


def _run_all_training_with_ui(self) -> None:
    if not _ensure_commands_ready(self):
        return
    self._run_all_training()


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


def _make_log_column(title_text: str, log_widget: QTextEdit) -> QWidget:
    box = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    label = QLabel(title_text)
    label.setStyleSheet("font-weight: 700; color: #cfe5ff; background: transparent;")
    layout.addWidget(label)
    layout.addWidget(log_widget, 1)
    box.setLayout(layout)
    return box


def _train_tab(self) -> QWidget:
    page = QVBoxLayout()
    page.setContentsMargins(10, 8, 10, 8)
    page.setSpacing(6)
    _connect_training_ui_signals(self)

    header = QVBoxLayout()
    header.setContentsMargins(2, 0, 2, 0)
    header.setSpacing(2)
    title = QLabel("Musubi LoRA Training")
    title.setStyleSheet("font-size: 14pt; font-weight: 800; color: #ffffff; background: transparent;")
    subtitle = QLabel(
        "Latent Cache → Text Cache → Train. Commands are prepared automatically; completed steps turn green."
        if _en(self)
        else "Latent Cache → Text Cache → 学習実行。必要なコマンド準備は自動化されています。成功した工程は緑になります。"
    )
    subtitle.setStyleSheet("color: #9fb4d0; background: transparent;")
    header.addWidget(title)
    header.addWidget(subtitle)
    page.addLayout(header)

    self.train_status = self._log()
    self.train_status.setVisible(False)
    self.command_preview = self._log()
    self.command_preview.setVisible(False)

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
    page.addWidget(_group(_txt(self, "1. 基本設定", "1. Basic Settings"), top_form))

    param_box = QVBoxLayout()
    param_box.setContentsMargins(8, 6, 8, 6)
    param_box.setSpacing(5)

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
    page.addWidget(_group(_txt(self, "2. 学習パラメータ", "2. Training Parameters"), param_box))

    run_row = QHBoxLayout()
    run_row.setSpacing(8)
    self.btn_latent_cache = self._button("1. Latent Cache", lambda: self._run_section_with_ui("latent_cache"))
    self.btn_text_cache = self._button("2. Text Cache", lambda: self._run_section_with_ui("text_cache"))
    self.btn_train = self._button(_txt(self, "3. 学習実行", "3. Train"), lambda: self._run_section_with_ui("train"))
    run_row.addWidget(self.btn_latent_cache)
    run_row.addWidget(self.btn_text_cache)
    run_row.addWidget(self.btn_train)
    run_row.addWidget(self._button(_txt(self, "全部実行", "Run All"), self._run_all_training_with_ui))
    run_row.addWidget(self._button(self.t("stop"), self._stop_process))
    run_row.addWidget(self._button(self.t("analyze_log"), lambda: self.analysis_log.setPlainText(self._analyze_current_logs())))
    run_row.addStretch()
    page.addWidget(_group(_txt(self, "3. 実行", "3. Run"), run_row))

    self.run_log = self._log()
    self.analysis_log = self._log()
    self.run_log.setMinimumHeight(220)
    self.analysis_log.setMinimumHeight(220)

    logs_row = QHBoxLayout()
    logs_row.setSpacing(8)
    logs_row.addWidget(_make_log_column(self.t("run_log"), self.run_log), 1)
    logs_row.addWidget(_make_log_column(self.t("error_analysis"), self.analysis_log), 1)
    page.addLayout(logs_row, 1)

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
    desktop_app_class._run_section_with_ui = _run_section_with_ui
    desktop_app_class._run_all_training_with_ui = _run_all_training_with_ui
    desktop_app_class._on_training_stage_finished_for_ui = _on_training_stage_finished_for_ui
