from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from caption_editor import bulk_replace_caption_rows, load_caption_rows, remove_words_caption_rows, save_caption_rows


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
        self._last_loaded_dataset_dir: str | None = None

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

        replace_row = QHBoxLayout()
        self.find_edit = QLineEdit()
        self.replace_edit = QLineEdit()
        self.replace_btn = QPushButton()
        self.replace_btn.clicked.connect(self.bulk_replace)
        replace_row.addWidget(QLabel("Find"))
        replace_row.addWidget(self.find_edit)
        replace_row.addWidget(QLabel("Replace"))
        replace_row.addWidget(self.replace_edit)
        replace_row.addWidget(self.replace_btn)
        box.addLayout(replace_row)

        remove_row = QHBoxLayout()
        self.remove_words_edit = QLineEdit()
        self.remove_words_btn = QPushButton()
        self.remove_words_btn.clicked.connect(self.remove_words)
        remove_row.addWidget(QLabel(_t(self.lang_getter(), "削除する語句", "Words to remove")))
        remove_row.addWidget(self.remove_words_edit)
        remove_row.addWidget(self.remove_words_btn)
        box.addLayout(remove_row)

        self.table = QTableWidget(0, 2)
        box.addWidget(self.table)

        box.addWidget(QLabel(_t(self.lang_getter(), "ログ", "Log")))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(120)
        box.addWidget(self.log)
        self.setLayout(box)
        self.refresh_language()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self.load_if_needed()

    def load_if_needed(self) -> None:
        dataset_dir = str(Path(self.dataset_dir_getter()))
        if dataset_dir != self._last_loaded_dataset_dir or self.table.rowCount() == 0:
            self.load_captions()

    def refresh_language(self) -> None:
        lang = self.lang_getter()
        self.load_btn.setText(_t(lang, "Captionを読み込み", "Load Captions"))
        self.save_btn.setText(_t(lang, "Captionを保存", "Save Captions"))
        self.reload_btn.setText(_t(lang, "再読み込み", "Reload"))
        self.replace_btn.setText(_t(lang, "一括置換", "Bulk Replace"))
        self.remove_words_btn.setText(_t(lang, "語句を一括削除", "Remove Words"))
        self.find_edit.setPlaceholderText(_t(lang, "探す文字列", "Find text"))
        self.replace_edit.setPlaceholderText(_t(lang, "置換後", "Replace with"))
        self.remove_words_edit.setPlaceholderText(_t(lang, "例: hair, background, clothes", "e.g. hair, background, clothes"))
        self.table.setHorizontalHeaderLabels([_t(lang, "画像", "Image"), "Caption"])
        self.guide.setPlainText(
            _t(
                lang,
                "Caption Editor\n\nDatasetタブで指定したフォルダの .txt caption を一覧表示します。\nこのタブを開くと自動で読み込みます。Caption列を直接編集して保存できます。一括置換や語句削除も使えます。画像ファイル名は変更しません。",
                "Caption Editor\n\nThis lists .txt captions in the folder selected on the Dataset tab.\nCaptions load automatically when this tab is opened. Edit captions directly, use bulk replace/remove, then save. Image filenames are not changed.",
            )
        )

    def _table_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for r in range(self.table.rowCount()):
            image_item = self.table.item(r, 0)
            caption_item = self.table.item(r, 1)
            rows.append([
                image_item.text() if image_item else "",
                caption_item.text() if caption_item else "",
            ])
        return rows

    def _set_table_rows(self, rows: list[list[str]]) -> None:
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            image = row[0] if len(row) > 0 else ""
            caption = row[1] if len(row) > 1 else ""
            img_item = QTableWidgetItem(image)
            img_item.setFlags(img_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, 0, img_item)
            self.table.setItem(r, 1, QTableWidgetItem(caption))
        self.table.resizeColumnsToContents()

    def load_captions(self) -> None:
        self.refresh_language()
        dataset_dir = Path(self.dataset_dir_getter())
        try:
            self.rows = load_caption_rows(dataset_dir)
            self._set_table_rows(self.rows)
            self._last_loaded_dataset_dir = str(dataset_dir)
            self.log.setPlainText(_t(self.lang_getter(), f"読み込み完了: {len(self.rows)}件", f"Loaded: {len(self.rows)} rows"))
        except Exception as exc:
            self.log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def save_captions(self) -> None:
        dataset_dir = Path(self.dataset_dir_getter())
        try:
            result = save_caption_rows(dataset_dir, self._table_rows())
            self.log.setPlainText(result)
        except Exception as exc:
            self.log.setPlainText(f"NG: {type(exc).__name__}: {exc}")

    def bulk_replace(self) -> None:
        rows = bulk_replace_caption_rows(self._table_rows(), self.find_edit.text(), self.replace_edit.text())
        self._set_table_rows(rows)
        self.log.setPlainText(_t(self.lang_getter(), "一括置換を適用しました。保存するにはCaptionを保存してください。", "Bulk replace applied. Click Save Captions to write files."))

    def remove_words(self) -> None:
        rows = remove_words_caption_rows(self._table_rows(), self.remove_words_edit.text())
        self._set_table_rows(rows)
        self.log.setPlainText(_t(self.lang_getter(), "語句削除を適用しました。保存するにはCaptionを保存してください。", "Word removal applied. Click Save Captions to write files."))
