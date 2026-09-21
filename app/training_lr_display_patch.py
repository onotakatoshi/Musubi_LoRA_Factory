from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QSpinBox

import training_tab_patch
from recommended_defaults import default_value, format_default, is_default_value


DETAIL_LABEL_MIN_WIDTH = 520
DETAIL_LABEL_MAX_WIDTH = 760


def apply_training_lr_display_patch() -> None:
    original_param_help = training_tab_patch._param_help
    original_en = training_tab_patch._en
    original_reason = training_tab_patch._training_reason

    def patched_training_param_row(self, name: str, widget: QSpinBox | QDoubleSpinBox) -> QHBoxLayout:
        from desktop_main import HelpLabel

        title = HelpLabel(training_tab_patch.DISPLAY_NAMES[name], original_param_help(self, name))
        title.setFixedWidth(118)
        title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        widget.setFixedWidth(96)

        reset_text = "Reset" if original_en(self) else "戻す"
        reset = self._button(reset_text, lambda: widget.setValue(default_value(name, self._current_profile_id())))
        reset.setObjectName("resetButton")
        reset.setToolTip("Reset to default" if original_en(self) else "デフォルトに戻す")
        reset.setFixedWidth(66 if original_en(self) else 64)
        reset.setFixedHeight(28)

        status = QLabel()
        status.setFixedWidth(72 if original_en(self) else 48)

        detail = QLabel()
        detail.setMinimumWidth(DETAIL_LABEL_MIN_WIDTH)
        detail.setMaximumWidth(DETAIL_LABEL_MAX_WIDTH)

        def refresh() -> None:
            # Read the profile on every refresh: switching Target model changes both the
            # recommended value shown here and whether the current value counts as one.
            profile_id = self._current_profile_id()
            shown = format_default(name, profile_id)
            reason = original_reason(name, self.lang)
            detail.setText(f"Default {shown}  {reason}" if original_en(self) else f"デフォルト {shown}　{reason}")
            if is_default_value(name, widget.value(), profile_id):
                status.setText("Default" if original_en(self) else "推奨")
            else:
                status.setText("Custom" if original_en(self) else "変更")

        widget.valueChanged.connect(lambda _value: refresh())
        if not hasattr(self, "_param_refreshers"):
            self._param_refreshers = []
        self._param_refreshers.append(refresh)
        refresh()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)
        row.addWidget(title)
        row.addWidget(widget)
        row.addWidget(reset)
        row.addWidget(status)
        row.addWidget(detail)
        row.addStretch(1)
        return row

    training_tab_patch._training_param_row = patched_training_param_row
