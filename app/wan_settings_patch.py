from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from settings_io import nested_get

WAN_HELP_JA = {
    "wan_vae": "Wan用VAEファイルです。例: Wan2.1_VAE.pth",
    "wan_t5": "Wan用Text Encoder/T5ファイルです。例: models_t5_umt5-xxl-enc-bf16.pth",
    "wan_dit": "Wan2.2のlow-noise側DiTです。t2v-A14Bでは主DiTとして使います。",
    "wan_dit_high_noise": "Wan2.2のhigh-noise側DiTです。指定するとhigh/low 2系統DiTで学習コマンドを作ります。",
}

WAN_HELP_EN = {
    "wan_vae": "Wan VAE file. Example: Wan2.1_VAE.pth",
    "wan_t5": "Wan Text Encoder/T5 file. Example: models_t5_umt5-xxl-enc-bf16.pth",
    "wan_dit": "Wan2.2 low-noise DiT. Used as the main DiT for t2v-A14B.",
    "wan_dit_high_noise": "Wan2.2 high-noise DiT. When set, commands use both high/low noise DiTs.",
}

WAN_LABELS = {
    "wan_vae": "Wan VAE",
    "wan_t5": "Wan T5",
    "wan_dit": "Wan2.2 DiT low noise",
    "wan_dit_high_noise": "Wan2.2 DiT high noise",
}


def _help(self, key: str) -> str:
    return (WAN_HELP_EN if getattr(self, "lang", "日本語") == "English" else WAN_HELP_JA)[key]


def apply_wan_settings_patch(desktop_app_class) -> None:
    original_settings_tab = desktop_app_class._settings_tab
    original_settings_data = desktop_app_class._settings_data_from_fields

    def patched_settings_tab(self):
        from desktop_main import HelpLabel

        widget = original_settings_tab(self)
        layout = widget.layout()
        if layout is None:
            return widget

        form = self._compact_form()
        self.set_wan_vae = self._line(nested_get(self.settings, "model_paths", "wan_vae"))
        self.set_wan_t5 = self._line(nested_get(self.settings, "model_paths", "wan_t5"))
        self.set_wan_dit = self._line(nested_get(self.settings, "model_paths", "wan_dit"))
        self.set_wan_dit_high_noise = self._line(nested_get(self.settings, "model_paths", "wan_dit_high_noise"))

        form.addRow(HelpLabel(WAN_LABELS["wan_vae"], _help(self, "wan_vae")), self._browse_file_row(self.set_wan_vae))
        form.addRow(HelpLabel(WAN_LABELS["wan_t5"], _help(self, "wan_t5")), self._browse_file_row(self.set_wan_t5))
        form.addRow(HelpLabel(WAN_LABELS["wan_dit"], _help(self, "wan_dit")), self._browse_file_row(self.set_wan_dit))
        form.addRow(HelpLabel(WAN_LABELS["wan_dit_high_noise"], _help(self, "wan_dit_high_noise")), self._browse_file_row(self.set_wan_dit_high_noise))

        group = QGroupBox("Wan2.2 Model Paths")
        group_layout = QVBoxLayout()
        group_layout.addLayout(form)
        group.setLayout(group_layout)

        insert_at = max(0, layout.count() - 1)
        layout.insertWidget(insert_at, group, 0)
        return widget

    def patched_settings_data_from_fields(self) -> dict:
        data = original_settings_data(self)
        model_paths = data.setdefault("model_paths", {})
        if hasattr(self, "set_wan_vae"):
            model_paths["wan_vae"] = self.set_wan_vae.text()
            model_paths["wan_t5"] = self.set_wan_t5.text()
            model_paths["wan_dit"] = self.set_wan_dit.text()
            model_paths["wan_dit_high_noise"] = self.set_wan_dit_high_noise.text()
        return data

    desktop_app_class._settings_tab = patched_settings_tab
    desktop_app_class._settings_data_from_fields = patched_settings_data_from_fields
