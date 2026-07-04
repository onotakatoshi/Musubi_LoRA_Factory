from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


PREFERRED_UI_FONTS = [
    "Noto Sans CJK JP",
    "Noto Sans JP",
    "Noto Sans CJK",
    "Noto Sans",
    "DejaVu Sans",
]


def choose_ui_font_family() -> str:
    families = set(QFontDatabase.families())
    for family in PREFERRED_UI_FONTS:
        if family in families:
            return family
    return QApplication.font().family()


def apply_balanced_ui_font(app: QApplication) -> str:
    family = choose_ui_font_family()
    font = QFont(family, 10)
    font.setWeight(QFont.Weight.Normal)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    app.setStyleSheet(
        """
        QWidget {
            font-family: "Noto Sans CJK JP", "Noto Sans JP", "Noto Sans CJK", "Noto Sans", "DejaVu Sans";
            font-size: 10pt;
            font-weight: 400;
        }
        QTabBar::tab {
            font-weight: 400;
        }
        QPushButton {
            background-color: #4a5563;
            color: #ffffff;
            border: 1px solid #313946;
            border-radius: 5px;
            padding: 6px 12px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #3f4a58;
        }
        QPushButton:pressed {
            background-color: #303946;
        }
        QPushButton:disabled {
            background-color: #a9aeb5;
            color: #eeeeee;
            border-color: #8f959d;
        }
        QLabel {
            font-weight: 400;
        }
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            font-weight: 400;
        }
        """
    )
    return family
