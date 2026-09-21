from __future__ import annotations

from PySide6.QtWidgets import QScrollArea, QTabWidget, QWidget

SPACER_TAB_INDEX = 2


def scrollable(widget: QWidget) -> QScrollArea:
    """Wrap a tab so a short window scrolls instead of clipping the bottom.

    The form-heavy tabs stack fixed-height groups and then a log area with a minimum
    height. Without a scroll area the tab cannot shrink below that sum, so on a smaller
    window the run log and error analysis panels were simply cut off at the bottom with
    no way to reach them.
    """
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QScrollArea.Shape.NoFrame)
    area.setWidget(widget)
    return area


def apply_tab_layout_patch(desktop_app_class) -> None:
    def patched_rebuild_ui(self) -> None:
        self.setWindowTitle(self.t("app_title"))
        tabs = QTabWidget()
        tabs.addTab(scrollable(self._settings_tab()), self.t("tab_settings"))
        tabs.addTab(scrollable(self._system_tab()), self.t("tab_system"))
        tabs.addTab(QWidget(), "")
        tabs.setTabEnabled(SPACER_TAB_INDEX, False)
        tabs.addTab(scrollable(self._dataset_tab()), self.t("tab_dataset"))
        # The caption table and the image preview are built to fill the tab and scroll
        # internally, so wrapping them would only add a second scrollbar.
        tabs.addTab(self._caption_tab(), self.t("tab_caption"))
        tabs.addTab(self._preview_tab(), self.t("tab_preview"))
        tabs.addTab(scrollable(self._config_tab()), self.t("tab_config"))
        tabs.addTab(scrollable(self._train_tab()), self.t("tab_train"))
        tabs.addTab(scrollable(self._export_tab()), self.t("tab_export"))
        self.setCentralWidget(tabs)

    desktop_app_class._rebuild_ui = patched_rebuild_ui
