from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from i18n import SUPPORTED_LANGUAGES
from model_registry import get_profile
from model_settings_catalog import MODEL_SETTINGS, all_model_path_keys, settings_spec
from model_ui import available_model_labels, help_for_profile, label_for_profile, profile_id_from_label, v1_default_profile
from settings_detect import validate_settings_paths
from settings_io import load_settings, nested_get

RIGHT_PANEL_TOP_OFFSET = 14
MODEL_NOTE_HEIGHT = 102
MODEL_GROUP_SPACING = 18
MODEL_PATH_GROUP_MIN_HEIGHT = 206


def _is_en(self) -> bool:
    return getattr(self, "lang", "日本語") == "English"


def _settings_profile_id(self) -> str:
    if hasattr(self, "set_target_model"):
        return profile_id_from_label(self.set_target_model.currentText())
    saved = nested_get(self.settings, "ui", "target_model", v1_default_profile().id)
    return saved or v1_default_profile().id


def _settings_intro_text(self, profile_id: str) -> str:
    profile = get_profile(profile_id)
    spec = settings_spec(profile_id)
    required = [field.label for field in spec.fields if field.required]
    required_text = ", ".join(required) if required else "(none)"
    if _is_en(self):
        return f"Settings / {profile.display_name}\nCheck the common paths, then set the required files on the right: {required_text}."
    return f"設定 / {profile.display_name}\n共通パスを確認し、右側で必要ファイルを指定します: {required_text}。"


def _field_help(self, profile_id: str, field_key: str) -> str:
    for field in settings_spec(profile_id).fields:
        if field.key == field_key:
            text = field.help_en if _is_en(self) else field.help_ja
            if not field.required:
                text += "\nOptional." if _is_en(self) else "\n任意設定です。"
            return text
    return field_key


def apply_wan_settings_patch(desktop_app_class) -> None:
    def refresh_model_settings_visibility(self) -> None:
        profile_id = _settings_profile_id(self)
        is_zimage = profile_id == "z-image"
        if hasattr(self, "settings_guide_box"):
            self.settings_guide_box.setPlainText(_settings_intro_text(self, profile_id))
        if hasattr(self, "model_setting_groups"):
            for group_profile_id, group in self.model_setting_groups.items():
                group.setVisible(group_profile_id == profile_id)
        if hasattr(self, "detect_zimage_button"):
            self.detect_zimage_button.setVisible(is_zimage)
        if hasattr(self, "model_settings_note"):
            self.model_settings_note.setPlainText(help_for_profile(profile_id, self.lang))

    def patched_settings_tab(self) -> QWidget:
        from desktop_main import HELP, HelpLabel

        box = QVBoxLayout()
        box.setContentsMargins(8, 8, 8, 8)
        box.setSpacing(6)

        self.settings_guide_box = QTextEdit()
        self.settings_guide_box.setReadOnly(True)
        self.settings_guide_box.setPlainText(_settings_intro_text(self, _settings_profile_id(self)))
        self.settings_guide_box.setMaximumHeight(64)
        box.addWidget(self.settings_guide_box, 0)

        common_form = self._compact_form()
        self.set_language = QComboBox()
        self.set_language.addItems(SUPPORTED_LANGUAGES)
        self.set_language.setCurrentText(self.lang)
        common_form.addRow(HelpLabel(self.t("language"), "UI language." if _is_en(self) else "UIの表示言語です。デフォルトは日本語です。"), self.set_language)

        self.set_target_model = QComboBox()
        self.set_target_model.addItems(available_model_labels())
        saved_profile = nested_get(self.settings, "ui", "target_model", v1_default_profile().id) or v1_default_profile().id
        self.set_target_model.setCurrentText(label_for_profile(saved_profile))
        common_form.addRow(HelpLabel("Target model", "Choose the model to configure and train." if _is_en(self) else "設定・学習対象のモデルです。選択に応じて必要なモデルパス欄だけ表示します。"), self.set_target_model)

        self.set_musubi_repo = self._line(nested_get(self.settings, "musubi", "repo_path"))
        common_form.addRow(HelpLabel(self.t("label_musubi_repo"), HELP["musubi_repo"]), self._browse_dir_row(self.set_musubi_repo))
        self.set_musubi_python = self._line(nested_get(self.settings, "musubi", "python_path"))
        common_form.addRow(HelpLabel(self.t("label_musubi_python"), HELP["musubi_python"]), self._browse_file_row(self.set_musubi_python))
        self.set_datasets_dir = self._line(nested_get(self.settings, "paths", "datasets_dir"))
        common_form.addRow(HelpLabel(self.t("label_datasets_dir"), HELP["datasets_dir"]), self._browse_dir_row(self.set_datasets_dir))
        self.set_outputs_dir = self._line(nested_get(self.settings, "paths", "outputs_dir"))
        common_form.addRow(HelpLabel(self.t("label_outputs_dir"), HELP["outputs_dir"]), self._browse_dir_row(self.set_outputs_dir))
        self.set_comfyui_loras_dir = self._line(nested_get(self.settings, "paths", "comfyui_loras_dir"))
        common_form.addRow(HelpLabel(self.t("label_comfyui_loras_dir"), HELP["comfyui_loras_dir"]), self._browse_dir_row(self.set_comfyui_loras_dir))

        common_group = QGroupBox("Common Settings" if _is_en(self) else "共通設定")
        common_layout = QVBoxLayout()
        common_layout.addLayout(common_form)
        common_group.setLayout(common_layout)

        self.model_settings_note = QTextEdit()
        self.model_settings_note.setReadOnly(True)
        self.model_settings_note.setMinimumHeight(MODEL_NOTE_HEIGHT)
        self.model_settings_note.setMaximumHeight(MODEL_NOTE_HEIGHT)

        self.model_path_fields = {}
        self.model_setting_groups = {}
        model_groups: list[QGroupBox] = []
        for profile_id, spec in MODEL_SETTINGS.items():
            model_form = self._compact_form()
            for item in spec.fields:
                line = self._line(nested_get(self.settings, "model_paths", item.key))
                self.model_path_fields[item.key] = line
                label = item.label if item.required else f"{item.label} (optional)"
                model_form.addRow(HelpLabel(label, _field_help(self, profile_id, item.key)), self._browse_file_row(line))
            group = QGroupBox(spec.group_title)
            group.setMinimumHeight(MODEL_PATH_GROUP_MIN_HEIGHT)
            group_layout = QVBoxLayout()
            group_layout.addLayout(model_form)
            group.setLayout(group_layout)
            self.model_setting_groups[profile_id] = group
            model_groups.append(group)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, RIGHT_PANEL_TOP_OFFSET, 0, 0)
        right_layout.setSpacing(MODEL_GROUP_SPACING)
        right_layout.addWidget(self.model_settings_note, 0)
        for group in model_groups:
            right_layout.addWidget(group, 0)
        right_layout.addStretch(1)
        right_panel.setLayout(right_layout)

        settings_row = QHBoxLayout()
        settings_row.setContentsMargins(0, 0, 0, 0)
        settings_row.setSpacing(8)
        settings_row.addWidget(common_group, 1)
        settings_row.addWidget(right_panel, 1)
        box.addLayout(settings_row, 0)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(self._button(self.t("validate_settings"), self._validate_settings))
        self.detect_zimage_button = self._button(self.t("detect_zimage_files"), self._detect_zimage_files)
        row.addWidget(self.detect_zimage_button)
        row.addWidget(self._button(self.t("save_settings"), self._save_settings))
        row.addWidget(self._button(self.t("reload_settings"), self._reload_settings_fields))
        row.addStretch()
        box.addLayout(row)

        self.settings_log = self._log()
        self.settings_log.setMinimumHeight(150)
        box.addWidget(self.settings_log, 1)

        self.set_target_model.currentTextChanged.connect(lambda _value: self._refresh_model_settings_visibility())
        w = QWidget()
        w.setLayout(box)
        self._refresh_model_settings_visibility()
        return w

    def patched_settings_values(self) -> dict[str, str]:
        values = {
            "musubi_repo": self.set_musubi_repo.text(),
            "musubi_python": self.set_musubi_python.text(),
            "datasets_dir": self.set_datasets_dir.text(),
            "outputs_dir": self.set_outputs_dir.text(),
            "comfyui_loras_dir": self.set_comfyui_loras_dir.text(),
        }
        for item in settings_spec(_settings_profile_id(self)).fields:
            if item.key in self.model_path_fields:
                values[item.key] = self.model_path_fields[item.key].text()
        return values

    def patched_validate_settings(self) -> None:
        self.settings_log.setPlainText(validate_settings_paths(self._settings_values(), _settings_profile_id(self)))

    def patched_settings_data_from_fields(self) -> dict:
        data = load_settings(__import__("desktop_main").SETTINGS_PATH)
        data.setdefault("ui", {})["language"] = self.set_language.currentText()
        data["ui"]["target_model"] = _settings_profile_id(self)
        data.setdefault("musubi", {})["repo_path"] = self.set_musubi_repo.text()
        data["musubi"]["python_path"] = self.set_musubi_python.text()
        data.setdefault("paths", {})["datasets_dir"] = self.set_datasets_dir.text()
        data["paths"]["outputs_dir"] = self.set_outputs_dir.text()
        data["paths"]["comfyui_loras_dir"] = self.set_comfyui_loras_dir.text()
        model_paths = data.setdefault("model_paths", {})
        for key in all_model_path_keys():
            if key in self.model_path_fields:
                model_paths[key] = self.model_path_fields[key].text()
        return data

    desktop_app_class._settings_tab = patched_settings_tab
    desktop_app_class._settings_values = patched_settings_values
    desktop_app_class._validate_settings = patched_validate_settings
    desktop_app_class._settings_data_from_fields = patched_settings_data_from_fields
    desktop_app_class._refresh_model_settings_visibility = refresh_model_settings_visibility
