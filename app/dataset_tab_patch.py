from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from settings_io import nested_get
from step_guides import guide
from training_presets import preset_names


DEFAULT_CONCEPT = "ono_style"
TRIGGER_FIELD_MIN_WIDTH = 460

TRIGGER_HELP_JA = (
    "LoRAを呼び出すための非常に重要な単語です。\n\n"
    "学習時: 各captionにこの語を入れて、学習したい人物・物体・特徴・画風と結びつけます。\n"
    "生成時: LoRAを読み込んだうえで、同じ語をpromptに入れると、そのLoRAの特徴を呼び出しやすくなります。\n\n"
    "複数指定もできます。カンマ区切りで入力してください。\n"
    "例: ono_style, blue_eye, soft_lighting\n\n"
    "おすすめは、まず固有で衝突しにくい主Triggerを1つ決めることです。"
    "必要に応じて補助Triggerを追加します。一般的すぎる語だけにすると既存概念と混ざりやすくなります。"
)
TRIGGER_HELP_EN = (
    "A very important word used to invoke the LoRA.\n\n"
    "During training: include this word in captions to bind it to the person, object, feature, or style you want to learn.\n"
    "During generation: load the LoRA, then include the same word in the prompt to invoke the learned concept more reliably.\n\n"
    "Multiple trigger words are supported. Separate them with commas.\n"
    "Example: ono_style, blue_eye, soft_lighting\n\n"
    "Recommended: choose one unique primary trigger first, then add optional secondary triggers only when needed. "
    "Very generic words can mix with existing model concepts."
)


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
        self.lora_type.setMinimumWidth(TRIGGER_FIELD_MIN_WIDTH)
        self.lora_type.setToolTip(TRIGGER_HELP_EN if self.lang == "English" else TRIGGER_HELP_JA)
        form.addRow(HelpLabel(self.t("label_lora_type"), TRIGGER_HELP_EN if self.lang == "English" else TRIGGER_HELP_JA), self.lora_type)
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
