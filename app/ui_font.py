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


MODERN_DARK_STYLESHEET = """
QWidget {
    background-color: #0b1020;
    color: #e8edf7;
    font-family: "Noto Sans CJK JP", "Noto Sans JP", "Noto Sans CJK", "Noto Sans", "DejaVu Sans";
    font-size: 10pt;
    font-weight: 400;
}

QMainWindow, QDialog {
    background-color: #0b1020;
}

QLabel {
    background: transparent;
    color: #dce6f7;
    font-weight: 400;
}

QGroupBox {
    background-color: #111827;
    border: 1px solid #243247;
    border-radius: 12px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
    color: #e8edf7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 8px;
    color: #9ad7ff;
    background-color: #111827;
    font-weight: 700;
}

QTabWidget::pane {
    border: 1px solid #243247;
    border-radius: 12px;
    background-color: #0f172a;
    top: -1px;
}

QTabBar::tab {
    background-color: #121a2b;
    color: #9aa8bd;
    border: 1px solid #25324a;
    border-bottom: none;
    padding: 9px 16px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1e2c44;
    color: #ffffff;
    border-color: #3b82f6;
}

QTabBar::tab:hover:!selected {
    background-color: #192338;
    color: #d6e4f8;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #78b7ff,
        stop:0.44 #3b82f6,
        stop:0.55 #1d4ed8,
        stop:1 #12317a);
    color: #ffffff;
    border: 1px solid #93c5fd;
    border-bottom: 2px solid #071a3d;
    border-right: 2px solid #071a3d;
    border-radius: 9px;
    padding: 7px 13px;
    font-weight: 800;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #bfdbfe,
        stop:0.44 #60a5fa,
        stop:0.55 #2563eb,
        stop:1 #1e40af);
    border: 1px solid #dbeafe;
    border-bottom: 2px solid #0b255f;
    border-right: 2px solid #0b255f;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f2f73,
        stop:1 #2563eb);
    border-top: 2px solid #06122c;
    border-left: 2px solid #06122c;
    border-bottom: 1px solid #93c5fd;
    border-right: 1px solid #93c5fd;
    padding-top: 8px;
    padding-left: 14px;
}

QPushButton:disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #64748b,
        stop:1 #334155);
    color: #cbd5e1;
    border: 1px solid #475569;
    border-bottom: 2px solid #1e293b;
    border-right: 2px solid #1e293b;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #020617;
    color: #e8edf7;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 8px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38bdf8;
    background-color: #07111f;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #e8edf7;
    border: 1px solid #334155;
    selection-background-color: #1e40af;
    selection-color: #ffffff;
    outline: none;
}

QTextEdit, QPlainTextEdit {
    background-color: #000000;
    color: #39ff88;
    border: 1px solid #0b7a3b;
    border-radius: 10px;
    padding: 10px;
    selection-background-color: #14532d;
    selection-color: #d9ffe8;
    font-family: "DejaVu Sans Mono", "Noto Sans Mono", "Ubuntu Mono", monospace;
    font-size: 9.7pt;
    line-height: 130%;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #22c55e;
    background-color: #000000;
}

QTextEdit QScrollBar:vertical, QPlainTextEdit QScrollBar:vertical {
    background-color: #020402;
}

QTextEdit QScrollBar::handle:vertical, QPlainTextEdit QScrollBar::handle:vertical {
    background-color: #0f7a3a;
}

QTextEdit QScrollBar::handle:vertical:hover, QPlainTextEdit QScrollBar::handle:vertical:hover {
    background-color: #16a34a;
}

QScrollBar:vertical {
    background-color: #0f172a;
    width: 12px;
    margin: 2px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 28px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0f172a;
    height: 12px;
    margin: 2px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #334155;
    min-width: 28px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #475569;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QProgressBar {
    background-color: #020617;
    border: 1px solid #334155;
    border-radius: 8px;
    text-align: center;
    color: #e8edf7;
}

QProgressBar::chunk {
    background-color: #22c55e;
    border-radius: 7px;
}

QSplitter::handle {
    background-color: #1e293b;
}

QToolTip {
    background-color: #111827;
    color: #e8edf7;
    border: 1px solid #38bdf8;
    border-radius: 6px;
    padding: 6px;
}
"""


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
    app.setStyleSheet(MODERN_DARK_STYLESHEET)
    return family
