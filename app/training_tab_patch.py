from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from model_ui import available_model_labels, help_for_profile, label_for_profile, v1_default_profile
from recommended_defaults import DEFAULTS, help_text as default_help_text
from step_guides import guide
from training_presets import preset_names


def _group(title: str, layout: QVBoxLayout | QFormLayout | QHBoxLayout) -> QGroupBox:
    box = QGroupBox(title)
    box.setLayout(layout)
    return box


def _train_tab(self) -> QWidget:
    page = QVBoxLayout()
    page.setContentsMargins(8, 8, 8, 8)
    page.setSpacing(8)

    guide_box = QTextEdit()
    guide_box.setReadOnly(True)
    guide_box.setPlainText(
        "操作順: 1) 設定を確認  2) コマンド確認  3) Latent Cache  4) Text Cache  5) 学習実行\n\n"
        + guide("train")
    )
    guide_box.setMaximumHeight(120)
    page.addWidget(guide_box)

    default_profile = v1_default_profile()
    settings_form = self._compact_form()
    self.target_model = QComboBox()
    self.target_model.addItems(available_model_labels())
    self.target_model.setCurrentText(label_for_profile(default_profile.id))
    self.target_model.currentTextChanged.connect(self._sync_profile_task)
    settings_form.addRow("Target model", self.target_model)

    self.task = QLineEdit(default_profile.task)
    self.task.setReadOnly(True)
    settings_form.addRow("Task", self.task)

    self.preset = QComboBox()
    self.preset.addItems(preset_names())
    if hasattr(self, "lora_type"):
        self.preset.setCurrentText(self.lora_type.currentText())
    settings_form.addRow("Preset", self.preset)

    self.rank = QSpinBox()
    self.rank.setRange(4, 128)
    self.rank.setSingleStep(4)
    self.rank.setValue(DEFAULTS["rank"])
    settings_form.addRow("Rank", self._default_spin_row("rank", self.rank))

    self.alpha = QSpinBox()
    self.alpha.setRange(4, 128)
    self.alpha.setSingleStep(4)
    self.alpha.setValue(DEFAULTS["alpha"])
    settings_form.addRow("Alpha", self._default_spin_row("alpha", self.alpha))

    self.epochs = QSpinBox()
    self.epochs.setRange(1, 100)
    self.epochs.setValue(DEFAULTS["epochs"])
    settings_form.addRow("Epochs", self._default_spin_row("epochs", self.epochs))

    self.lr = QDoubleSpinBox()
    self.lr.setDecimals(8)
    self.lr.setRange(0.000001, 0.01)
    self.lr.setSingleStep(0.00001)
    self.lr.setValue(DEFAULTS["lr"])
    settings_form.addRow("Learning rate", self._default_spin_row("lr", self.lr))

    self.output_name = self._line("zimage_smoke_test")
    settings_form.addRow("Output name", self.output_name)
    page.addWidget(_group("1. 学習設定", settings_form))

    prepare_row = QHBoxLayout()
    prepare_row.setSpacing(6)
    prepare_row.addWidget(self._button("Preset適用", self._apply_preset))
    prepare_row.addWidget(self._button("学習前レビュー", self._training_review))
    prepare_row.addWidget(self._button(self.t("preflight_check"), self._preflight))
    prepare_row.addWidget(self._button(self.t("preview_commands"), self._preview_commands))
    prepare_row.addWidget(self._button(self.t("estimate_training_load"), self._estimate_training_load))
    prepare_row.addStretch()
    page.addWidget(_group("2. 確認・準備", prepare_row))

    run_row = QHBoxLayout()
    run_row.setSpacing(6)
    run_row.addWidget(self._button("1. Latent Cache", lambda: self._run_section("latent_cache")))
    run_row.addWidget(self._button("2. Text Cache", lambda: self._run_section("text_cache")))
    run_row.addWidget(self._button("3. 学習実行", lambda: self._run_section("train")))
    run_row.addWidget(self._button("全部実行", self._run_all_training))
    run_row.addWidget(self._button(self.t("stop"), self._stop_process))
    run_row.addWidget(self._button(self.t("analyze_log"), lambda: self.analysis_log.setPlainText(self._analyze_current_logs())))
    run_row.addStretch()
    page.addWidget(_group("3. 実行", run_row))

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
