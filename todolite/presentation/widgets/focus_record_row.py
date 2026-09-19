from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...domain.focus import FocusSession
from ..formatters import format_duration
from .icon_button import IconButton
from .elided_label import ElidedLabel


class FocusRecordRow(QWidget):
    def __init__(
        self,
        session: FocusSession,
        on_delete: Callable[[str], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 6, 5)
        layout.setSpacing(8)

        text = ElidedLabel(session.name)
        text.setObjectName("TaskText")
        text.setToolTip(session.name)
        timestamp = QLabel(session.ended_at[:16].replace('T', ' '))
        timestamp.setObjectName("MutedText")
        info = QVBoxLayout()
        info.setSpacing(3)
        info.addWidget(text)
        info.addWidget(timestamp)

        duration = QLabel(format_duration(session.duration_seconds))
        duration.setObjectName("RecordDuration")
        duration.setToolTip("专注时长")

        delete_button = IconButton(
            "×", "删除专注记录", "删除专注记录", dangerous=True, parent=self
        )
        delete_button.clicked.connect(lambda: on_delete(session.id))

        layout.addLayout(info, 1)
        layout.addWidget(duration, 0)
        layout.addWidget(delete_button, 0)
