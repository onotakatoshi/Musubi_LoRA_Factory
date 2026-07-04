from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QWidget


SPACER_TAB_INDEX = 2


def apply_tab_layout_patch(desktop_app_class) -> None:
    def patched_rebuild_ui(self) -> None:
        self.setWindowTitle(self.t("app_title"))
        tabs = QTabWidget()
        tabs.addTab(self._settings_tab(), self.t("tab_settings"))
        tabs.addTab(self._system_tab(), self.t("tab_system"))
        tabs.addTab(QWidget(), "")
        tabs.setTabEnabled(SPACER_TAB_INDEX, False)
        tabs.addTab(self._dataset_tab(), self.t("tab_dataset"))
        tabs.addTab(self._caption_tab(), self.t("tab_caption"))
        tabs.addTab(self._preview_tab(), self.t("tab_preview"))
        tabs.addTab(self._config_tab(), self.t("tab_config"))
        tabs.addTab(self._train_tab(), self.t("tab_train"))
        tabs.addTab(self._export_tab(), self.t("tab_export"))
        self.setCentralWidget(tabs)

    desktop_app_class._rebuild_ui = patched_rebuild_ui
