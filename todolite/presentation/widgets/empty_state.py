from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from .sprout import Sprout


class EmptyState(QWidget):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("EmptyStatePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(4)
        layout.addStretch()
        layout.addWidget(Sprout(48), 0, Qt.AlignHCenter)
        label = QLabel(text)
        label.setObjectName("EmptyState")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch()
