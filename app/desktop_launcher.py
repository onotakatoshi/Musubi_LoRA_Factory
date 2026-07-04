from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from desktop_main import DesktopApp
from ui_font import apply_balanced_ui_font


def main() -> int:
    app = QApplication(sys.argv)
    apply_balanced_ui_font(app)
    win = DesktopApp()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
