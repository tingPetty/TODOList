from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

from ...domain.task import Task
from .icon_button import IconButton


class TaskTextLabel(QLabel):
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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(8)

        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.setFixedWidth(20)
        checkbox.setToolTip("标记任务完成")
        checkbox.setAccessibleName("标记任务完成")
        checkbox.toggled.connect(lambda checked: on_toggle(self.task_id, checked))

        self.text_label = TaskTextLabel(self._display_text(task))
        self.text_label.setObjectName("TaskText")
        self.text_label.setToolTip("双击编辑任务")
        self.text_label.doubleClicked.connect(lambda: on_edit(self.task_id))
        self._apply_completed_style(task.completed)

        delete_button = IconButton(
            "×", "删除任务", "删除任务", dangerous=True, parent=self
        )
        delete_button.clicked.connect(lambda: on_delete(self.task_id))

        layout.addWidget(checkbox, 0)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(delete_button, 0)

    def _display_text(self, task: Task) -> str:
        return f"❗ {task.text}" if task.important else task.text

    def _apply_completed_style(self, completed: bool) -> None:
        font = self.text_label.font()
        font.setStrikeOut(completed)
        font.setBold(self.important)
        self.text_label.setFont(font)
        self.text_label.setStyleSheet(
            "color: rgba(203, 213, 225, 140);"
            if completed
            else "color: #e2e8f0;"
        )
