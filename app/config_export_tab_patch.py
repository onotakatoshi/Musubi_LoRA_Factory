from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from recommended_defaults import DEFAULTS
from settings_io import nested_get
from step_guides import guide


def apply_config_export_tab_patch(desktop_app_class) -> None:
    def patched_config_tab(self) -> QWidget:
        from desktop_main import HELP, HelpLabel, config_status

        box = QVBoxLayout()
        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setPlainText(guide("config", self.lang))
        guide_box.setMaximumHeight(160)
        box.addWidget(guide_box)

        form = self._compact_form()
        self.output_dir = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage"))
        form.addRow(HelpLabel(self.t("label_output_folder"), HELP["output_folder"]), self._browse_dir_row(self.output_dir))
        self.resolution = QSpinBox()
        self.resolution.setRange(256, 2048)
        self.resolution.setSingleStep(64)
        self.resolution.setValue(DEFAULTS["resolution"])
        form.addRow(HelpLabel(self.t("label_resolution"), "Training image resolution." if self.lang == "English" else "学習画像の解像度です。"), self._default_spin_row("resolution", self.resolution))
        self.dataset_toml = self._line("")
        form.addRow(HelpLabel(self.t("label_dataset_toml"), HELP["dataset_toml"]), self.dataset_toml)
        box.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addWidget(self._button(self.t("build_dataset_toml"), self._build_dataset_toml))
        buttons.addWidget(self._button(self.t("check_current_step"), lambda: self.config_log.setPlainText(config_status(self.dataset_toml.text()))))
        buttons.addStretch()
        box.addLayout(buttons)

        self.config_log = self._log()
        box.addWidget(self.config_log)
        w = QWidget()
        w.setLayout(box)
        return w

    def patched_export_tab(self) -> QWidget:
        from desktop_main import HelpLabel

        box = QVBoxLayout()
        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setPlainText(guide("export", self.lang))
        guide_box.setMaximumHeight(160)
        box.addWidget(guide_box)

        self.lora_path = self._line(str(Path(nested_get(self.settings, "paths", "outputs_dir")) / "Eye_Blue_v1_zimage" / "eye_lora_zimage.safetensors"))
        box.addLayout(self._browse_file_row(self.lora_path))

        row = QHBoxLayout()
        row.addWidget(self._button("コピー前チェック" if self.lang != "English" else "Pre-copy Check", self._validate_export))
        row.addWidget(self._button(self.t("copy_to_comfyui"), self._copy_lora))
        row.addStretch()
        box.addLayout(row)

        self.export_log = self._log()
        box.addWidget(self.export_log)
        w = QWidget()
        w.setLayout(box)
        return w

    desktop_app_class._config_tab = patched_config_tab
    desktop_app_class._export_tab = patched_export_tab
