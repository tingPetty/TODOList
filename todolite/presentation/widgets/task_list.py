from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QListWidget


ITEM_TYPE_ROLE = Qt.UserRole + 1
TASK_ID_ROLE = Qt.UserRole + 2
TASK_DATE_ROLE = Qt.UserRole + 3
TASK_COMPLETED_ROLE = Qt.UserRole + 4


class TaskListWidget(QListWidget):
    reordered = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, event):  # noqa: N802
        super().dropEvent(event)
        self.reordered.emit()
