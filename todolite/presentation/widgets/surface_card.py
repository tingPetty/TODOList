from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout


class SurfaceCard(QFrame):
    """Shared translucent card container for both top-level pages."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SurfaceCard")
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(12, 10, 12, 10)
        self.body.setSpacing(8)
