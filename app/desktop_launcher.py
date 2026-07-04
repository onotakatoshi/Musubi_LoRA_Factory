from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from desktop_main import DesktopApp
from training_engine import TrainingEngine
from training_engine_patch import apply_training_engine_patch
from training_tab_patch import apply_training_tab_patch
from ui_font import apply_balanced_ui_font


apply_training_engine_patch(TrainingEngine)
apply_training_tab_patch(DesktopApp)


def main() -> int:
    app = QApplication(sys.argv)
    apply_balanced_ui_font(app)
    win = DesktopApp()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
