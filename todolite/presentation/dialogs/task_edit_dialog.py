from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from ...domain.task import Task


class TaskEditDialog(QDialog):
    def __init__(self, parent, task: Task) -> None:
        super().__init__(parent)
        self.setObjectName("LightDialog")
        self.setWindowTitle("编辑任务")
        self.setModal(True)
        self.resize(340, 160)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.text_input = QLineEdit(task.text)
        self.text_input.setPlaceholderText("任务内容")

        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        date = QDate.fromString(task.task_date, "yyyy-MM-dd")
        self.date_edit.setDate(date if date.isValid() else QDate.currentDate())

        self.important_check = QCheckBox("重要任务")
        self.important_check.setChecked(task.important)

        form.addRow("内容", self.text_input)
        form.addRow("日期", self.date_edit)
        form.addRow("标记", self.important_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root.addLayout(form)
        root.addWidget(buttons)

    def accept(self) -> None:
        if not self.text_input.text().strip():
            QMessageBox.warning(self, "编辑任务", "任务内容不能为空")
            return
        super().accept()

    def values(self) -> tuple[str, str, bool]:
        return (
            self.text_input.text().strip(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.important_check.isChecked(),
        )
