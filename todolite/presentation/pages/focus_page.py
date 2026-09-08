from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from ...services.focus_service import FocusService
from ..formatters import format_duration
from ..styles.metrics import PAGE_MARGIN, SECTION_SPACING
from ..widgets.icon_button import IconButton
from ..widgets.surface_card import SurfaceCard


class FocusPage(QWidget):
    def __init__(
        self,
        focus_service: FocusService,
        on_show_history: Callable[[], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.focus_service = focus_service
        self.on_show_history = on_show_history
        self.setObjectName("FocusPage")
        self._build_ui()

        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        root.setSpacing(SECTION_SPACING)

        card = SurfaceCard()
        header = QHBoxLayout()
        title = QLabel("◷ 专注空间")
        title.setObjectName("PageTitle")
        history_button = IconButton("▤", "专注历史", "专注历史")
        history_button.clicked.connect(self.on_show_history)
        header.addWidget(title, 1)
        header.addWidget(history_button)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("这次准备专注什么？")
        self.name_input.returnPressed.connect(self._start)
        self.start_button = IconButton("▶", "开始专注", "开始专注", primary=True)
        self.start_button.clicked.connect(self._start)

        start_row = QHBoxLayout()
        start_row.setSpacing(8)
        start_row.addWidget(self.name_input, 1)
        start_row.addWidget(self.start_button)

        self.session_name = QLabel("")
        self.session_name.setObjectName("FocusName")
        self.session_name.setAlignment(Qt.AlignCenter)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("FocusTimer")
        self.timer_label.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setObjectName("MutedText")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.pause_button = IconButton("Ⅱ", "暂停专注", "暂停专注")
        self.pause_button.clicked.connect(self._pause_or_resume)
        self.finish_button = IconButton("■", "结束并保存", "结束并保存", stop=True)
        self.finish_button.clicked.connect(self._finish)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.addStretch(1)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.finish_button)
        controls.addStretch(1)

        card.body.addLayout(header)
        card.body.addLayout(start_row)
        card.body.addSpacing(6)
        card.body.addWidget(self.session_name)
        card.body.addWidget(self.timer_label)
        card.body.addWidget(self.status_label)
        card.body.addLayout(controls)
        card.body.addStretch(1)
        root.addWidget(card, 1)

    def refresh(self) -> None:
        status = self.focus_service.status
        active = status in {"running", "paused"}
        self.name_input.setVisible(not active)
        self.start_button.setVisible(not active)
        self.session_name.setVisible(active)
        self.pause_button.setVisible(active)
        self.finish_button.setVisible(active)
        self.timer_label.setText(
            format_duration(self.focus_service.current_elapsed_seconds())
        )
        self.session_name.setText(self.focus_service.current_name)
        if status == "running":
            self.status_label.setText("专注进行中")
            self.pause_button.setText("Ⅱ")
            self.pause_button.setToolTip("暂停专注")
            self.pause_button.setAccessibleName("暂停专注")
        elif status == "paused":
            self.status_label.setText("已暂停，可继续")
            self.pause_button.setText("▶")
            self.pause_button.setToolTip("继续专注")
            self.pause_button.setAccessibleName("继续专注")
        else:
            self.status_label.setText("准备好后开始一段专注")

    def _start(self) -> None:
        try:
            self.focus_service.start(self.name_input.text())
        except ValueError:
            self.status_label.setText("请先填写专注名称")
            return
        self.name_input.clear()
        self.refresh()

    def _pause_or_resume(self) -> None:
        if self.focus_service.status == "running":
            self.focus_service.pause()
        elif self.focus_service.status == "paused":
            self.focus_service.resume()
        self.refresh()

    def _finish(self) -> None:
        if self.focus_service.status not in {"running", "paused"}:
            return
        self.focus_service.finish()
        self.refresh()
