from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTabWidget

from desktop_main import DesktopApp


EXPECTED_TAB_KEYWORDS = [
    "設定",
    "システム",
    "データセット",
    "Caption編集",
    "画像プレビュー",
    "コンフィグ生成",
    "学習",
    "書き出し",
]


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    win = DesktopApp()
    tabs = win.centralWidget()
    assert isinstance(tabs, QTabWidget)
    labels = [tabs.tabText(i) for i in range(tabs.count())]
    for expected in EXPECTED_TAB_KEYWORDS:
        assert any(expected in label for label in labels), f"missing tab keyword: {expected}; labels={labels}"
    assert win.windowTitle()
    win.close()
    app.processEvents()
    print("Desktop launch smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
