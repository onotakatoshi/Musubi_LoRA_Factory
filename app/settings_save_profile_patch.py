from __future__ import annotations

from env_check import check_environment
from i18n import normalize_language
from settings_io import nested_get, save_settings


def apply_settings_save_profile_patch(desktop_app_class) -> None:
    def patched_save_settings(self) -> None:
        try:
            import desktop_main

            data = self._settings_data_from_fields()
            profile_id = nested_get(data, "ui", "target_model", "z-image") or "z-image"
            save_settings(desktop_main.SETTINGS_PATH, data)
            self.settings = data
            self.lang = normalize_language(nested_get(data, "ui", "language", "日本語"))
            self._rebuild_ui()
            self.settings_log.setPlainText(
                f"{self.t('settings_saved')}: {desktop_main.SETTINGS_PATH}\n\n"
                + check_environment(desktop_main.SETTINGS_PATH, profile_id)
            )
        except Exception as exc:
            self.settings_log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    desktop_app_class._save_settings = patched_save_settings
