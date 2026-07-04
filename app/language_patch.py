from __future__ import annotations

from i18n import normalize_language
from settings_io import nested_get, save_settings


def apply_language_patch(desktop_app_class) -> None:
    original_settings_tab = desktop_app_class._settings_tab

    def change_language_immediately(self, value: str) -> None:
        new_lang = normalize_language(value)
        if new_lang == getattr(self, "lang", "日本語"):
            return
        data = self._settings_data_from_fields()
        data.setdefault("ui", {})["language"] = new_lang
        import desktop_main

        save_settings(desktop_main.SETTINGS_PATH, data)
        self.settings = data
        self.lang = normalize_language(nested_get(data, "ui", "language", new_lang))
        self._rebuild_ui()

    def patched_settings_tab(self):
        widget = original_settings_tab(self)
        if hasattr(self, "set_language"):
            self.set_language.currentTextChanged.connect(lambda value: self._change_language_immediately(value))
        return widget

    desktop_app_class._settings_tab = patched_settings_tab
    desktop_app_class._change_language_immediately = change_language_immediately
