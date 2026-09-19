from __future__ import annotations

from collections.abc import Callable
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from ...services.focus_service import FocusService
from ..formatters import format_duration
from ..widgets.icon_button import IconButton
from ..widgets.surface_card import SurfaceCard
from ..widgets.sprout import Sprout
from ..widgets.elided_label import ElidedLabel


class FocusPage(QWidget):
    def __init__(self, focus_service: FocusService, on_show_history: Callable[[], None], parent=None):
        super().__init__(parent)
        self.focus_service = focus_service
        self.on_show_history = on_show_history
        self._error = False
        self._saved = False
        self._saved_elapsed = 0
        self._last_status = None
        self.setObjectName("FocusPage")
        self._build_ui()
        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self._clear_feedback)
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        card = SurfaceCard()
        card.body.setSpacing(6)
        header = QHBoxLayout()
        title = QLabel("专注空间")
        title.setObjectName("PageTitle")
        history = IconButton("history", "专注历史")
        history.clicked.connect(self.on_show_history)
        header.addWidget(title, 1)
        header.addWidget(history)
        card.body.addLayout(header)
        card.body.addStretch(1)

        self.sprout = Sprout(64)
        card.body.addWidget(self.sprout, 0, Qt.AlignHCenter)
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("FocusTimer")
        self.timer_label.setAlignment(Qt.AlignCenter)
        card.body.addWidget(self.timer_label)

        self.session_name = ElidedLabel()
        self.session_name.setObjectName("FocusName")
        self.session_name.setAlignment(Qt.AlignCenter)
        card.body.addWidget(self.session_name)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("这次准备专注什么？")
        self.name_input.setAccessibleName("专注名称")
        self.name_input.returnPressed.connect(self._start)
        self.name_input.textEdited.connect(self._clear_feedback)
        card.body.addWidget(self.name_input)

        self.status_label = QLabel()
        self.status_label.setObjectName("MutedText")
        self.status_label.setAlignment(Qt.AlignCenter)
        card.body.addWidget(self.status_label)

        self.start_button = IconButton("play", "开始专注", primary=True)
        self.start_button.set_label("开始专注", 120)
        self.start_button.clicked.connect(self._start)
        self.pause_button = IconButton("pause", "暂停专注")
        self.pause_button.set_label("暂停", 88)
        self.pause_button.clicked.connect(self._pause_or_resume)
        self.finish_button = IconButton("stop", "结束并保存", stop=True)
        self.finish_button.set_label("结束并保存", 130)
        self.finish_button.clicked.connect(self._finish)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.addStretch()
        controls.addWidget(self.start_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.finish_button)
        controls.addStretch()
        card.body.addLayout(controls)
        card.body.addStretch(1)
        root.addWidget(card)

    def _clear_feedback(self):
        self._error = False
        self._saved = False
        self.refresh()

    def refresh(self):
        status = self.focus_service.status
        active = status in {"running", "paused"}
        elapsed = self.focus_service.current_elapsed_seconds()
        self.timer_label.setText(format_duration(elapsed))
        if status != self._last_status:
            self._last_status = status
            self.name_input.setVisible(not active)
            self.start_button.setVisible(not active)
            self.session_name.setVisible(active)
            self.pause_button.setVisible(active)
            self.finish_button.setVisible(active)
            self.session_name.setText(self.focus_service.current_name)
            self.session_name.setToolTip(self.focus_service.current_name)
            paused = status == "paused"
            self.pause_button.set_symbol("play" if paused else "pause")
            self.pause_button.set_label("继续" if paused else "暂停", 88)
            self.pause_button.setToolTip("继续专注" if paused else "暂停专注")
            self.pause_button.setAccessibleName(self.pause_button.toolTip())
        self.sprout.set_state(
            "happy" if self._saved and not active else status,
            self._saved_elapsed if self._saved and not active else elapsed,
        )
        message = ("请先填写专注名称" if self._error else
                   "已保存这段专注，辛苦啦" if self._saved else
                   "正在专注 · 小芽陪着你" if status == "running" else
                   "已暂停，休息一下再继续" if status == "paused" else
                   "从一小段专注开始")
        self.status_label.setText(message)
        name = "ErrorText" if self._error else "MutedText"
        if self.status_label.objectName() != name:
            self.status_label.setObjectName(name)
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        compact = self.height() < 300 or self.width() < 350
        self.sprout.setFixedSize(40 if compact else 64, 40 if compact else 64)
        if self.timer_label.property("compact") != compact:
            self.timer_label.setProperty("compact", compact)
            self.timer_label.style().unpolish(self.timer_label)
            self.timer_label.style().polish(self.timer_label)

    def _start(self):
        if self.focus_service.status != "idle":
            return
        try:
            self.focus_service.start(self.name_input.text())
        except ValueError:
            self._error = True
            self.refresh()
            self.name_input.setFocus()
            return
        self._error = self._saved = False
        self.feedback_timer.stop()
        self.name_input.clear()
        self.refresh()

    def _pause_or_resume(self):
        if self.focus_service.status == "running":
            self.focus_service.pause()
        elif self.focus_service.status == "paused":
            self.focus_service.resume()
        self.refresh()

    def _finish(self):
        if self.focus_service.status not in {"running", "paused"}:
            return
        self._saved_elapsed = self.focus_service.current_elapsed_seconds()
        self.focus_service.finish()
        self._saved = True
        self.feedback_timer.start(2500)
        self.refresh()
