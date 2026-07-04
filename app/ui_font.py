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
        QTabWidget::pane {
            border: 1px solid #7a7f87;
            background: #f4f5f7;
            top: -1px;
        }
        QTabBar::tab {
            background: #5f6670;
            color: #ffffff;
            border: 1px solid #4b515a;
            border-bottom: none;
            padding: 7px 13px;
            margin-right: 2px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background: #2f3742;
            color: #ffffff;
            border-color: #2a3039;
        }
        QTabBar::tab:hover:!selected {
            background: #4f5660;
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
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            border: 1px solid #9aa1aa;
            border-radius: 4px;
            padding: 3px 5px;
            font-weight: 400;
        }
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #4a5563;
        }
        """
    )
    return family
