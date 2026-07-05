from __future__ import annotations

from PySide6.QtWidgets import QLabel

import training_tab_patch
from model_ui import help_for_profile, label_for_profile, profile_id_from_label, v1_default_profile
from settings_io import nested_get

TRAINING_MODEL_NOTE_STYLE = "color: #cfe5ff; background: transparent; padding: 2px 4px;"


def _settings_profile_id(self) -> str:
    if hasattr(self, "set_target_model"):
        return profile_id_from_label(self.set_target_model.currentText())
    return nested_get(getattr(self, "settings", {}), "ui", "target_model", v1_default_profile().id) or v1_default_profile().id


def _update_training_model_note(self) -> None:
    if not hasattr(self, "target_model"):
        return
    profile_id = profile_id_from_label(self.target_model.currentText())
    text = help_for_profile(profile_id, getattr(self, "lang", "日本語"))
    self.target_model.setToolTip(text)
    if hasattr(self, "training_model_note"):
        self.training_model_note.setText(text.replace("\n\n", "  /  ").replace("\n", "  /  "))
        self.training_model_note.setToolTip(text)


def _sync_training_target_from_settings(self) -> None:
    if not hasattr(self, "target_model"):
        return
    profile_id = _settings_profile_id(self)
    label = label_for_profile(profile_id)
    if self.target_model.currentText() != label:
        self.target_model.setCurrentText(label)
    else:
        self._sync_profile_task()
    _update_training_model_note(self)


def apply_model_sync_patch(desktop_app_class) -> None:
    training_tab_patch.BASIC_HELP_JA["target_model"] = "学習対象のモデルです。SettingsのTarget modelと連動し、選択モデルに応じてtaskとコマンドが切り替わります。"
    training_tab_patch.BASIC_HELP_EN["target_model"] = "Model to train. This follows the Settings Target model and controls the task and generated commands."
    training_tab_patch.BASIC_HELP_JA["output_name"] = "作成されるLoRAファイル名の元になります。例: smoke_test → smoke_test.safetensors。"
    training_tab_patch.BASIC_HELP_EN["output_name"] = "Base name for the generated LoRA file. Example: smoke_test becomes smoke_test.safetensors."

    original_sync_profile_task = desktop_app_class._sync_profile_task

    def patched_sync_profile_task(self) -> None:
        original_sync_profile_task(self)
        _update_training_model_note(self)

    desktop_app_class._sync_profile_task = patched_sync_profile_task

    original_train_tab = desktop_app_class._train_tab

    def patched_train_tab(self):
        widget = original_train_tab(self)
        layout = widget.layout()
        if layout is not None:
            self.training_model_note = QLabel()
            self.training_model_note.setWordWrap(True)
            self.training_model_note.setMaximumHeight(54)
            self.training_model_note.setStyleSheet(TRAINING_MODEL_NOTE_STYLE)
            layout.insertWidget(2, self.training_model_note, 0)
            _update_training_model_note(self)
        return widget

    desktop_app_class._train_tab = patched_train_tab

    original_refresh = getattr(desktop_app_class, "_refresh_model_settings_visibility", None)

    def patched_refresh_model_settings_visibility(self) -> None:
        if original_refresh is not None:
            original_refresh(self)
        _sync_training_target_from_settings(self)

    desktop_app_class._refresh_model_settings_visibility = patched_refresh_model_settings_visibility
