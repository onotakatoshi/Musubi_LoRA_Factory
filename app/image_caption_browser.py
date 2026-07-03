from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pipeline import image_files


def _t(lang: str, ja: str, en: str) -> str:
    return en if lang == "English" else ja


class ImageCaptionBrowser(QWidget):
    """Image preview + single-caption editor.

    This is meant for careful visual review: click an image, preview it, edit the
    caption, and save only that caption. It complements the bulk caption table.
    """

    def __init__(self, dataset_dir_getter: Callable[[], str], lang_getter: Callable[[], str]):
        super().__init__()
        self.dataset_dir_getter = dataset_dir_getter
        self.lang_getter = lang_getter
        self.current_image: Path | None = None
        self.dirty = False
        self._loading = False

        root = QVBoxLayout()
        self.guide = QTextEdit()
        self.guide.setReadOnly(True)
        self.guide.setMaximumHeight(95)
        root.addWidget(self.guide)

        toolbar = QHBoxLayout()
        self.reload_btn = QPushButton()
        self.save_btn = QPushButton()
        self.fit_btn = QPushButton("Fit")
        self.zoom100_btn = QPushButton("100%")
        self.reload_btn.clicked.connect(self.load_images)
        self.save_btn.clicked.connect(self.save_current_caption)
        self.fit_btn.clicked.connect(lambda: self.show_current_image(fit=True))
        self.zoom100_btn.clicked.connect(lambda: self.show_current_image(fit=False))
        toolbar.addWidget(self.reload_btn)
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(self.fit_btn)
        toolbar.addWidget(self.zoom100_btn)
        toolbar.addStretch()
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        splitter.addWidget(self.list_widget)

        right = QWidget()
        right_layout = QVBoxLayout()
        self.status = QLabel()
        right_layout.addWidget(self.status)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(360)
        self.image_label.setStyleSheet("border: 1px solid #888; background: #222;")
        right_layout.addWidget(self.image_label)
        self.caption_edit = QTextEdit()
        self.caption_edit.textChanged.connect(self.on_caption_changed)
        right_layout.addWidget(self.caption_edit)
        right.setLayout(right_layout)
        splitter.addWidget(right)
        splitter.setSizes([280, 880])
        root.addWidget(splitter)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(100)
        root.addWidget(self.log)
        self.setLayout(root)
        self.refresh_language()

    def refresh_language(self) -> None:
        lang = self.lang_getter()
        self.reload_btn.setText(_t(lang, "画像を読み込み", "Load Images"))
        self.save_btn.setText(_t(lang, "現在のCaptionを保存", "Save Current Caption"))
        self.guide.setPlainText(
            _t(
                lang,
                "画像プレビュー\n\n画像をクリックするとプレビューとcaptionを表示します。captionを編集すると未保存表示になります。\n一覧表で一括編集し、この画面で画像を見ながら最終確認する使い方を想定しています。",
                "Image Preview\n\nClick an image to show the preview and caption. Editing the caption marks it as unsaved.\nUse the table for bulk edits, then this view for visual review.",
            )
        )
        self._update_status()

    def load_images(self) -> None:
        self.refresh_language()
        dataset_dir = Path(self.dataset_dir_getter())
        self.list_widget.clear()
        self.current_image = None
        self.caption_edit.clear()
        self.image_label.clear()
        self.dirty = False
        imgs = image_files(dataset_dir)
        for img in imgs:
            item = QListWidgetItem(img.name)
            item.setData(Qt.ItemDataRole.UserRole, str(img))
            self.list_widget.addItem(item)
        self.log.setPlainText(_t(self.lang_getter(), f"画像を読み込みました: {len(imgs)}件", f"Loaded images: {len(imgs)}"))
        if imgs:
            self.list_widget.setCurrentRow(0)

    def maybe_save_before_switch(self) -> bool:
        if not self.dirty:
            return True
        # Initial version keeps this conservative: do not auto-save on switch.
        self.log.setPlainText(_t(self.lang_getter(), "未保存のcaptionがあります。先に保存してください。", "Unsaved caption. Save it before switching."))
        return False

    def on_current_item_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        if previous is not None and self.dirty:
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentItem(previous)
            self.list_widget.blockSignals(False)
            self.maybe_save_before_switch()
            return
        path = Path(current.data(Qt.ItemDataRole.UserRole))
        self.current_image = path
        self.load_current_caption()
        self.show_current_image(fit=True)
        self.dirty = False
        self._update_status()

    def load_current_caption(self) -> None:
        if not self.current_image:
            return
        txt = self.current_image.with_suffix(".txt")
        caption = txt.read_text(encoding="utf-8").strip() if txt.exists() else ""
        self._loading = True
        self.caption_edit.setPlainText(caption)
        self._loading = False

    def show_current_image(self, fit: bool = True) -> None:
        if not self.current_image:
            return
        pix = QPixmap(str(self.current_image))
        if pix.isNull():
            self.image_label.setText(_t(self.lang_getter(), "画像を表示できません", "Could not load image"))
            return
        if fit:
            pix = pix.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pix)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self.show_current_image(fit=True)

    def on_caption_changed(self) -> None:
        if self._loading:
            return
        if self.current_image:
            self.dirty = True
            self._update_status()

    def save_current_caption(self) -> None:
        if not self.current_image:
            self.log.setPlainText(_t(self.lang_getter(), "画像が選択されていません。", "No image selected."))
            return
        txt = self.current_image.with_suffix(".txt")
        txt.write_text(self.caption_edit.toPlainText().strip() + "\n", encoding="utf-8")
        self.dirty = False
        self._update_status()
        self.log.setPlainText(_t(self.lang_getter(), f"保存しました: {txt.name}", f"Saved: {txt.name}"))

    def _update_status(self) -> None:
        lang = self.lang_getter()
        name = self.current_image.name if self.current_image else _t(lang, "未選択", "No selection")
        dirty = " ● 未保存" if self.dirty and lang != "English" else " ● Unsaved" if self.dirty else ""
        self.status.setText(f"{name}{dirty}")
