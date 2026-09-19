from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from ...domain.task import Task
from ..styles.controls import style_date_picker


class TaskEditDialog(QDialog):
    def __init__(self, parent, task: Task) -> None:
        super().__init__(parent)
        self.setObjectName("LightDialog")
        self.setWindowTitle("编辑任务")
        self.setModal(True)
        self.resize(370, 235)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)
        form = QFormLayout()

        self.text_input = QLineEdit(task.text)
        self.text_input.setPlaceholderText("任务内容")

        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        style_date_picker(self.date_edit)
        date = QDate.fromString(task.task_date, "yyyy-MM-dd")
        self.date_edit.setDate(date if date.isValid() else QDate.currentDate())

        self.important_check = QCheckBox("重要任务")
        self.important_check.setChecked(task.important)

        form.addRow("内容", self.text_input)
        form.addRow("日期", self.date_edit)
        form.addRow("标记", self.important_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("保存")
        buttons.button(QDialogButtonBox.Ok).setObjectName("PrimaryButton")
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root.addLayout(form)
        self.error_label = QLabel("任务内容不能为空")
        self.error_label.setObjectName("ErrorText")
        self.error_label.hide()
        self.text_input.textEdited.connect(lambda: self.error_label.hide())
        root.addWidget(self.error_label)
        root.addWidget(buttons)

    def accept(self) -> None:
        if not self.text_input.text().strip():
            self.error_label.show()
            self.text_input.setFocus()
            return
        super().accept()

    def values(self) -> tuple[str, str, bool]:
        return (
            self.text_input.text().strip(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.important_check.isChecked(),
        )
