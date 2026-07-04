from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from settings_io import nested_get
from step_guides import guide
from training_presets import preset_names


DEFAULT_CONCEPT = "eye"


def apply_dataset_tab_patch(desktop_app_class) -> None:
    def patched_dataset_tab(self) -> QWidget:
        from desktop_main import HELP, HelpLabel

        box = QVBoxLayout()
        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setPlainText(guide("dataset"))
        guide_box.setMaximumHeight(190)
        box.addWidget(guide_box)

        form = self._compact_form()
        self.dataset_dir = self._line(str(Path(nested_get(self.settings, "paths", "datasets_dir")) / "Eye_Blue_v1"))
        form.addRow(HelpLabel(self.t("label_dataset_folder"), HELP["dataset_folder"]), self._browse_dir_row(self.dataset_dir))

        self.lora_type = QComboBox()
        self.lora_type.setEditable(True)
        self.lora_type.addItems(preset_names())
        self.lora_type.setCurrentText(DEFAULT_CONCEPT)
        self.lora_type.setToolTip(
            "自由に入力できます。例: character_name, blue_eye, my_style, product_logo"
            if self.lang != "English"
            else "Editable. Examples: character_name, blue_eye, my_style, product_logo"
        )
        form.addRow(HelpLabel(self.t("label_lora_type"), HELP["lora_type"]), self.lora_type)
        box.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addWidget(self._button(self.t("check_dataset"), self._check_dataset))
        buttons.addWidget(self._button(self.t("diagnose_captions"), self._diagnose_captions))
        buttons.addWidget(self._button(self.t("check_current_step"), self._dataset_status))
        buttons.addStretch()
        box.addLayout(buttons)

        self.dataset_log = self._log()
        box.addWidget(self.dataset_log)
        w = QWidget()
        w.setLayout(box)
        return w

    desktop_app_class._dataset_tab = patched_dataset_tab
