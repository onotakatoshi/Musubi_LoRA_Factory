from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import Qt, QProcess, QProcessEnvironment
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
from captioning import build_caption_prompt, qwen_vl_caption_command
from path_resolver import resolve_path
from process_env import subprocess_env_overrides
from settings_io import nested_get


def _t(lang: str, ja: str, en: str) -> str:
    return en if lang == "English" else ja


class CaptionTableWidget(QWidget):
    """Simple caption table for the initial desktop app.

    It intentionally edits only the .txt captions next to images. This keeps the
    first version safe and easy to understand.
    """

    def __init__(
        self,
        dataset_dir_getter: Callable[[], str],
        lang_getter: Callable[[], str],
        settings_getter: Callable[[], dict[str, Any]] | None = None,
    ):
        super().__init__()
        self.dataset_dir_getter = dataset_dir_getter
        self.lang_getter = lang_getter
        self.settings_getter = settings_getter
        self.rows: list[list[str]] = []
        self._last_loaded_dataset_dir: str | None = None
        self.caption_process: QProcess | None = None

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
        self.subject_term_edit = QLineEdit()
        self.subject_term_edit.setMaximumWidth(180)
        if settings_getter is not None:
            self.subject_term_edit.setText(nested_get(settings_getter(), "caption", "subject_term"))
        self.generate_btn = QPushButton()
        self.generate_btn.clicked.connect(self.generate_captions)
        buttons.addWidget(self.load_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.reload_btn)
        self.subject_term_label = QLabel()
        buttons.addWidget(self.subject_term_label)
        buttons.addWidget(self.subject_term_edit)
        buttons.addWidget(self.generate_btn)
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
        self.load_btn.setText(_t(lang, "キャプションを読み込み", "Load Captions"))
        self.save_btn.setText(_t(lang, "キャプションを保存", "Save Captions"))
        self.reload_btn.setText(_t(lang, "再読み込み", "Reload"))
        self.generate_btn.setText(_t(lang, "キャプション生成 (Qwen2.5-VL)", "Generate Captions (Qwen2.5-VL)"))
        self.subject_term_label.setText(_t(lang, "主題の語", "Subject term"))
        self.subject_term_edit.setPlaceholderText(_t(lang, "例: marmot", "e.g. marmot"))
        self.subject_term_edit.setToolTip(
            _t(
                lang,
                "キャプション内で主題をこの語に固定します。空欄だと画像ごとに別の同義語が使われ、1つの概念が複数の語に分散します。",
                "Pins the subject to this word. Left empty, the captioner picks a different synonym per image and one concept ends up split across tokens.",
            )
        )
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

    def _append_log(self, text: str) -> None:
        self.log.setPlainText((self.log.toPlainText() + text)[-8000:])
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def generate_captions(self) -> None:
        """Run musubi-tuner's Qwen2.5-VL captioner over the dataset folder.

        It writes one .txt next to each image, so the table just needs a reload when
        the process finishes.
        """
        lang = self.lang_getter()
        if self.caption_process is not None:
            self._append_log(_t(lang, "\n生成はすでに実行中です。\n", "\nCaption generation is already running.\n"))
            return
        if self.settings_getter is None:
            self.log.setPlainText(_t(lang, "NG: 設定を参照できません。", "NG: settings are not available."))
            return

        settings = self.settings_getter()
        model_path = nested_get(settings, "caption", "qwen_vl_model_path")
        if not model_path:
            self.log.setPlainText(
                _t(
                    lang,
                    "NG: 設定タブの caption.qwen_vl_model_path が未設定です。\n"
                    "Qwen2.5-VL系のチェックポイント（例: Qwen-Image の text_encoder/model-00001-of-00004.safetensors）を指定してください。",
                    "NG: caption.qwen_vl_model_path is not set.\n"
                    "Point it at a Qwen2.5-VL checkpoint, e.g. Qwen-Image's text_encoder/model-00001-of-00004.safetensors.",
                )
            )
            return

        dataset_dir = resolve_path(self.dataset_dir_getter())
        subject_term = self.subject_term_edit.text().strip()
        command = qwen_vl_caption_command(
            musubi_python=resolve_path(nested_get(settings, "musubi", "python_path")),
            musubi_repo=resolve_path(nested_get(settings, "musubi", "repo_path")),
            image_dir=dataset_dir,
            model_path=resolve_path(model_path),
            prompt=build_caption_prompt(subject_term, nested_get(settings, "caption", "prompt")),
        )

        env = QProcessEnvironment.systemEnvironment()
        for key, value in subprocess_env_overrides().items():
            env.insert(key, value)

        self.log.setPlainText(_t(lang, f"キャプション生成を開始します:\n{command}\n", f"Starting caption generation:\n{command}\n"))
        self.generate_btn.setEnabled(False)
        process = QProcess(self)
        process.setProcessEnvironment(env)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyReadStandardOutput.connect(self._on_caption_output)
        process.finished.connect(self._on_caption_finished)
        self.caption_process = process
        process.start("bash", ["-lc", command])

    def _on_caption_output(self) -> None:
        if self.caption_process is None:
            return
        data = self.caption_process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        if data:
            self._append_log(data)

    def _on_caption_finished(self, exit_code: int, _status) -> None:
        self.caption_process = None
        self.generate_btn.setEnabled(True)
        lang = self.lang_getter()
        if exit_code == 0:
            self._append_log(_t(lang, "\n生成完了。キャプションを読み込み直します。\n", "\nDone. Reloading captions.\n"))
            self.load_captions()
        else:
            self._append_log(_t(lang, f"\nNG: 生成が失敗しました (exit {exit_code})\n", f"\nNG: caption generation failed (exit {exit_code})\n"))

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
        self.log.setPlainText(_t(self.lang_getter(), "一括置換を適用しました。保存するにはキャプションを保存してください。", "Bulk replace applied. Click Save Captions to write files."))

    def remove_words(self) -> None:
        rows = remove_words_caption_rows(self._table_rows(), self.remove_words_edit.text())
        self._set_table_rows(rows)
        self.log.setPlainText(_t(self.lang_getter(), "語句削除を適用しました。保存するにはキャプションを保存してください。", "Word removal applied. Click Save Captions to write files."))
