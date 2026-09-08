from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


class EmptyState(QLabel):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("EmptyState")
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
