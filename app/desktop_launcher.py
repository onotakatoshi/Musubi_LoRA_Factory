from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from button_i18n_patch import apply_button_i18n_patch
from config_export_tab_patch import apply_config_export_tab_patch
from dataset_tab_patch import apply_dataset_tab_patch
from desktop_main import DesktopApp, HelpLabel
from help_label_patch import apply_help_label_patch
from language_patch import apply_language_patch as apply_ui_language_patch
from tab_layout_patch import apply_tab_layout_patch
from training_engine import TrainingEngine
from training_engine_patch import apply_training_engine_patch
from training_lr_display_patch import apply_training_lr_display_patch
from training_tab_patch import apply_training_tab_patch
from ui_font import apply_balanced_ui_font
from wan_settings_patch import apply_wan_settings_patch


ROOT = Path(__file__).resolve().parents[1]
ICON_PATH = ROOT / "assets" / "icons" / "musubi_lora_factory.svg"

apply_help_label_patch(HelpLabel)
apply_training_engine_patch(TrainingEngine)
apply_training_lr_display_patch()
apply_button_i18n_patch(DesktopApp)
apply_dataset_tab_patch(DesktopApp)
apply_config_export_tab_patch(DesktopApp)
apply_training_tab_patch(DesktopApp)
apply_wan_settings_patch(DesktopApp)
apply_tab_layout_patch(DesktopApp)
apply_ui_language_patch(DesktopApp)


def main() -> int:
    app = QApplication(sys.argv)
    apply_balanced_ui_font(app)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    win = DesktopApp()
    if ICON_PATH.exists():
        win.setWindowIcon(QIcon(str(ICON_PATH)))
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
