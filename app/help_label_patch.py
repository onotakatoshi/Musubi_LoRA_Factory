from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMessageBox


HELP_MARK_HTML = '<span style="color:#f59e0b; font-weight:900;">?</span>'


def apply_help_label_patch(help_label_class) -> None:
    def patched_init(self, text: str, help_text: str):
        QLabel.__init__(self)
        self.label_text = text
        self.help_text = help_text
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setText(f"{escape(text)}&nbsp;&nbsp;{HELP_MARK_HTML}")
        self.setToolTip(help_text)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)

    def patched_mouse_press_event(self, event):
        QMessageBox.information(self, getattr(self, "label_text", "Help"), self.help_text)

    help_label_class.__init__ = patched_init
    help_label_class.mousePressEvent = patched_mouse_press_event
