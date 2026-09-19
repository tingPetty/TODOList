from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

from ...domain.task import Task
from .icon_button import IconButton
from .elided_label import ElidedLabel
from ..styles.icons import ui_icon


class TaskTextLabel(ElidedLabel):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):  # noqa: N802
        self.doubleClicked.emit()
        event.accept()


class TaskRow(QWidget):
    def __init__(
        self,
        task: Task,
        on_toggle: Callable[[str, bool], None],
        on_delete: Callable[[str], None],
        on_edit: Callable[[str], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.task_id = task.id
        self.important = task.important
        self.setMinimumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(8)

        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.setFixedWidth(28)
        checkbox.setToolTip("标记任务完成")
        checkbox.setAccessibleName("标记任务完成")
        checkbox.toggled.connect(lambda checked: on_toggle(self.task_id, checked))

        self.text_label = TaskTextLabel(self._display_text(task))
        self.text_label.setObjectName("TaskText")
        self.text_label.setToolTip(f"{task.text}\n双击编辑任务")
        self.text_label.doubleClicked.connect(lambda: on_edit(self.task_id))
        self._apply_completed_style(task.completed)

        delete_button = IconButton(
            "×", "删除任务", "删除任务", dangerous=True, parent=self
        )
        delete_button.clicked.connect(lambda: on_delete(self.task_id))

        layout.addWidget(checkbox, 0)
        layout.addWidget(self.text_label, 1)
        if task.important:
            star = QLabel()
            star.setPixmap(ui_icon("star").pixmap(16, 16))
            star.setToolTip("重要任务")
            star.setAccessibleName("重要任务")
            layout.addWidget(star)
        layout.addWidget(delete_button, 0)

    def _display_text(self, task: Task) -> str:
        return task.text

    def _apply_completed_style(self, completed: bool) -> None:
        font = self.text_label.font()
        font.setStrikeOut(completed)
        font.setBold(self.important)
        self.text_label.setFont(font)
        self.text_label.setProperty("completed", completed)
