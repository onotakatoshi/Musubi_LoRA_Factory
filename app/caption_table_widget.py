from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from caption_editor import load_caption_rows, save_caption_rows


def _t(lang: str, ja: str, en: str) -> str:
    return en if lang == "English" else ja


class CaptionTableWidget(QWidget):
    """Simple caption table for the initial desktop app.

    It intentionally edits only the .txt captions next to images. This keeps the
    first version safe and easy to understand.
    """

    def __init__(self, dataset_dir_getter: Callable[[], str], lang_getter: Callable[[], str]):
        super().__init__()
        self.dataset_dir_getter = dataset_dir_getter
        self.lang_getter = lang_getter
        self.rows: list[list[str]] = []

        box = QVBoxLayout()
        self.guide = QTextEdit()
        self.guide.setReadOnly(True)
        self.guide.setMaximumHeight(120)
        box.addWidget(self.guide)

        buttons = QHBoxLayout()
        self.load_btn = QPushButton()
        self.save_btn = QPushButton()
        self.reload_btn = QPushButton()
        self.load_btn.clicked.connect(self.load_captions)
        self.save_btn.clicked.connect(self.save_captions)
        self.reload_btn.clicked.connect(self.load_captions)
        buttons.addWidget(self.load_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.reload_btn)
        buttons.addStretch()
        box.addLayout(buttons)

        self.table = QTableWidget(0, 2)
        box.addWidget(self.table)

        box.addWidget(QLabel(_t(self.lang_getter(), "ログ", "Log")))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(120)
        box.addWidget(self.log)
        self.setLayout(box)
        self.refresh_language()

    def refresh_language(self) -> None:
        lang = self.lang_getter()
        self.load_btn.setText(_t(lang, "Captionを読み込み", "Load Captions"))
        self.save_btn.setText(_t(lang, "Captionを保存", "Save Captions"))
        self.reload_btn.setText(_t(lang, "再読み込み", "Reload"))
        self.table.setHorizontalHeaderLabels([_t(lang, "画像", "Image"), "Caption"])
        self.guide.setPlainText(
            _t(
                lang,
                "Caption Editor\n\nDatasetタブで指定したフォルダの .txt caption を一覧表示します。\nCaption列を直接編集して、保存できます。画像ファイル名は変更しません。",
                "Caption Editor\n\nThis lists .txt captions in the folder selected on the Dataset tab.\nEdit the Caption column directly, then save. Image filenames are not changed.",
            )
        )

    def load_captions(self) -> None:
        self.refresh_language()
        dataset_dir = Path(self.dataset_dir_getter())
        try:
            self.rows = load_caption_rows(dataset_dir)
            self.table.setRowCount(len(self.rows))
            for r, row in enumerate(self.rows):
                image = row[0] if len(row) > 0 else ""
                caption = row[1] if len(row) > 1 else ""
                img_item = QTableWidgetItem(image)
                img_item.setFlags(img_item.flags() & ~img_item.flags().ItemIsEditable)
                self.table.setItem(r, 0, img_item)
                self.table.setItem(r, 1, QTableWidgetItem(caption))
            self.table.resizeColumnsToContents()
            self.log.setPlainText(_t(self.lang_getter(), f"読み込み完了: {len(self.rows)}件", f"Loaded: {len(self.rows)} rows"))
        except Exception as exc:
            self.log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def save_captions(self) -> None:
        dataset_dir = Path(self.dataset_dir_getter())
        rows: list[list[str]] = []
        for r in range(self.table.rowCount()):
            image_item = self.table.item(r, 0)
            caption_item = self.table.item(r, 1)
            rows.append([
                image_item.text() if image_item else "",
                caption_item.text() if caption_item else "",
            ])
        try:
            result = save_caption_rows(dataset_dir, rows)
            self.log.setPlainText(result)
        except Exception as exc:
            self.log.setPlainText(f"NG: {type(exc).__name__}: {exc}")
