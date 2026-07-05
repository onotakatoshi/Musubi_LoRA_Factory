from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from i18n import SUPPORTED_LANGUAGES
from model_ui import available_model_labels, help_for_profile, label_for_profile, profile_id_from_label, v1_default_profile
from settings_detect import validate_settings_paths
from settings_io import load_settings, nested_get

ZIMAGE_HELP_JA = {
    "zimage_dit": "Z-Imageの学習対象DiTです。BaseまたはDe-Turbo系を指定します。",
    "zimage_vae": "Z-Image用VAEファイルです。",
    "zimage_text_encoder": "Z-Image用Text Encoderです。",
    "zimage_base_weights": "任意設定です。必要な場合だけ指定します。",
}
ZIMAGE_HELP_EN = {
    "zimage_dit": "Z-Image DiT to train. Usually use Base or De-Turbo weights.",
    "zimage_vae": "Z-Image VAE file.",
    "zimage_text_encoder": "Z-Image text encoder file.",
    "zimage_base_weights": "Optional base weights. Set only when needed.",
}

WAN_HELP_JA = {
    "wan_vae": "Wan用VAEファイルです。例: Wan2.1_VAE.pth",
    "wan_t5": "Wan用Text Encoder/T5ファイルです。例: models_t5_umt5-xxl-enc-bf16.pth",
    "wan_dit": "Wan2.2のlow-noise側DiTです。t2v-A14Bの2系統DiT構成で必要です。",
    "wan_dit_high_noise": "Wan2.2のhigh-noise側DiTです。t2v-A14Bではlow-noise側とセットで必要です。",
}
WAN_HELP_EN = {
    "wan_vae": "Wan VAE file. Example: Wan2.1_VAE.pth",
    "wan_t5": "Wan Text Encoder/T5 file. Example: models_t5_umt5-xxl-enc-bf16.pth",
    "wan_dit": "Wan2.2 low-noise DiT. Required for the t2v-A14B dual-DiT setup.",
    "wan_dit_high_noise": "Wan2.2 high-noise DiT. Required together with the low-noise DiT for t2v-A14B.",
}

ZIMAGE_LABELS = {
    "zimage_dit": "Z-Image DiT",
    "zimage_vae": "Z-Image VAE",
    "zimage_text_encoder": "Z-Image text encoder",
    "zimage_base_weights": "Z-Image base weights",
}
WAN_LABELS = {
    "wan_vae": "Wan VAE",
    "wan_t5": "Wan T5",
    "wan_dit": "Wan2.2 DiT low noise",
    "wan_dit_high_noise": "Wan2.2 DiT high noise",
}


def _is_en(self) -> bool:
    return getattr(self, "lang", "日本語") == "English"


def _z_help(self, key: str) -> str:
    return (ZIMAGE_HELP_EN if _is_en(self) else ZIMAGE_HELP_JA)[key]


def _wan_help(self, key: str) -> str:
    return (WAN_HELP_EN if _is_en(self) else WAN_HELP_JA)[key]


def _settings_profile_id(self) -> str:
    if hasattr(self, "set_target_model"):
        return profile_id_from_label(self.set_target_model.currentText())
    saved = nested_get(self.settings, "ui", "target_model", v1_default_profile().id)
    return saved or v1_default_profile().id


def _settings_intro_text(self, profile_id: str) -> str:
    if _is_en(self):
        if profile_id == "wan2.2":
            return "Settings / Wan2.2\nConfigure common paths, then set four required files on the right: Wan VAE, Wan T5, Wan2.2 low-noise DiT, and Wan2.2 high-noise DiT."
        return "Settings / Z-Image / Z-Image-Turbo\nConfigure the common paths, then set the Z-Image DiT, VAE, and Text Encoder paths on the right. Selecting Z-Image also synchronizes the Train tab target model."
    if profile_id == "wan2.2":
        return "設定 / Wan2.2\n共通パスを確認し、右側で必要な4ファイルを指定します: Wan VAE、Wan T5、Wan2.2 DiT low noise、Wan2.2 DiT high noise。"
    return "設定 / Z-Image / Z-Image-Turbo\n共通パスを確認し、右側で Z-Image DiT、VAE、Text Encoder を指定します。Z-Imageを選ぶと、学習タブのTarget modelもZ-Imageへ同期します。"


def apply_wan_settings_patch(desktop_app_class) -> None:
    def refresh_model_settings_visibility(self) -> None:
        profile_id = _settings_profile_id(self)
        is_zimage = profile_id == "z-image"
        if hasattr(self, "settings_guide_box"):
            self.settings_guide_box.setPlainText(_settings_intro_text(self, profile_id))
        if hasattr(self, "zimage_settings_group"):
            self.zimage_settings_group.setVisible(is_zimage)
        if hasattr(self, "wan_settings_group"):
            self.wan_settings_group.setVisible(profile_id == "wan2.2")
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
        self.model_settings_note.setMaximumHeight(74)

        z_form = self._compact_form()
        self.set_zimage_dit = self._line(nested_get(self.settings, "model_paths", "zimage_dit"))
        self.set_zimage_vae = self._line(nested_get(self.settings, "model_paths", "zimage_vae"))
        self.set_zimage_text_encoder = self._line(nested_get(self.settings, "model_paths", "zimage_text_encoder"))
        self.set_zimage_base_weights = self._line(nested_get(self.settings, "model_paths", "zimage_base_weights"))
        z_form.addRow(HelpLabel(ZIMAGE_LABELS["zimage_dit"], _z_help(self, "zimage_dit")), self._browse_file_row(self.set_zimage_dit))
        z_form.addRow(HelpLabel(ZIMAGE_LABELS["zimage_vae"], _z_help(self, "zimage_vae")), self._browse_file_row(self.set_zimage_vae))
        z_form.addRow(HelpLabel(ZIMAGE_LABELS["zimage_text_encoder"], _z_help(self, "zimage_text_encoder")), self._browse_file_row(self.set_zimage_text_encoder))
        z_form.addRow(HelpLabel(ZIMAGE_LABELS["zimage_base_weights"], _z_help(self, "zimage_base_weights")), self._browse_file_row(self.set_zimage_base_weights))
        self.zimage_settings_group = QGroupBox("Z-Image / Z-Image-Turbo Model Paths")
        z_layout = QVBoxLayout()
        z_layout.addLayout(z_form)
        self.zimage_settings_group.setLayout(z_layout)

        wan_form = self._compact_form()
        self.set_wan_vae = self._line(nested_get(self.settings, "model_paths", "wan_vae"))
        self.set_wan_t5 = self._line(nested_get(self.settings, "model_paths", "wan_t5"))
        self.set_wan_dit = self._line(nested_get(self.settings, "model_paths", "wan_dit"))
        self.set_wan_dit_high_noise = self._line(nested_get(self.settings, "model_paths", "wan_dit_high_noise"))
        wan_form.addRow(HelpLabel(WAN_LABELS["wan_vae"], _wan_help(self, "wan_vae")), self._browse_file_row(self.set_wan_vae))
        wan_form.addRow(HelpLabel(WAN_LABELS["wan_t5"], _wan_help(self, "wan_t5")), self._browse_file_row(self.set_wan_t5))
        wan_form.addRow(HelpLabel(WAN_LABELS["wan_dit"], _wan_help(self, "wan_dit")), self._browse_file_row(self.set_wan_dit))
        wan_form.addRow(HelpLabel(WAN_LABELS["wan_dit_high_noise"], _wan_help(self, "wan_dit_high_noise")), self._browse_file_row(self.set_wan_dit_high_noise))
        self.wan_settings_group = QGroupBox("Wan2.2 Model Paths")
        wan_layout = QVBoxLayout()
        wan_layout.addLayout(wan_form)
        self.wan_settings_group.setLayout(wan_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(self.model_settings_note, 0)
        right_layout.addWidget(self.zimage_settings_group, 0)
        right_layout.addWidget(self.wan_settings_group, 0)
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
        profile_id = _settings_profile_id(self)
        if profile_id == "wan2.2":
            values.update({
                "wan_vae": self.set_wan_vae.text(),
                "wan_t5": self.set_wan_t5.text(),
                "wan_dit": self.set_wan_dit.text(),
                "wan_dit_high_noise": self.set_wan_dit_high_noise.text(),
            })
        else:
            values.update({
                "zimage_dit": self.set_zimage_dit.text(),
                "zimage_vae": self.set_zimage_vae.text(),
                "zimage_text_encoder": self.set_zimage_text_encoder.text(),
                "zimage_base_weights": self.set_zimage_base_weights.text(),
            })
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
        model_paths["zimage_dit"] = self.set_zimage_dit.text()
        model_paths["zimage_vae"] = self.set_zimage_vae.text()
        model_paths["zimage_text_encoder"] = self.set_zimage_text_encoder.text()
        model_paths["zimage_base_weights"] = self.set_zimage_base_weights.text()
        model_paths["wan_vae"] = self.set_wan_vae.text()
        model_paths["wan_t5"] = self.set_wan_t5.text()
        model_paths["wan_dit"] = self.set_wan_dit.text()
        model_paths["wan_dit_high_noise"] = self.set_wan_dit_high_noise.text()
        return data

    desktop_app_class._settings_tab = patched_settings_tab
    desktop_app_class._settings_values = patched_settings_values
    desktop_app_class._validate_settings = patched_validate_settings
    desktop_app_class._settings_data_from_fields = patched_settings_data_from_fields
    desktop_app_class._refresh_model_settings_visibility = refresh_model_settings_visibility
