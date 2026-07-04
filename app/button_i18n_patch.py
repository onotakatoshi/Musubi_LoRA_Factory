from __future__ import annotations

BUTTON_LABELS_EN = {
    "コピー前チェック": "Pre-copy Check",
    "全部実行": "Run All",
    "Preset適用": "Apply Preset",
    "学習前レビュー": "Training Review",
    "Project保存": "Save Project",
    "Project読み込み": "Load Project",
}


def apply_button_i18n_patch(desktop_app_class) -> None:
    original_button = desktop_app_class._button

    def patched_button(self, text: str, fn):
        if getattr(self, "lang", "日本語") == "English":
            text = BUTTON_LABELS_EN.get(text, text)
        return original_button(self, text, fn)

    desktop_app_class._button = patched_button
