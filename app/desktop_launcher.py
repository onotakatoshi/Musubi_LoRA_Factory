from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from desktop_main import DesktopApp
from training_engine import TrainingEngine
from training_engine_patch import apply_training_engine_patch
from training_tab_patch import apply_training_tab_patch
from ui_font import apply_balanced_ui_font


ROOT = Path(__file__).resolve().parents[1]
ICON_PATH = ROOT / "assets" / "icons" / "musubi_lora_factory.svg"

apply_training_engine_patch(TrainingEngine)
apply_training_tab_patch(DesktopApp)


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
