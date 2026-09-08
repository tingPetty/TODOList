from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizeGrip


class ResizeGrip(QSizeGrip):
    """A visible bottom-right handle for resizing the frameless main window."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.SizeFDiagCursor)
        self.setToolTip("拖动调整窗口大小")
        self.setAccessibleName("调整窗口大小")
        self._press_position: QPoint | None = None
        self._start_size = None

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._press_position = event.globalPosition().toPoint()
            self._start_size = self.window().size()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._press_position is not None and self._start_size is not None:
            delta = event.globalPosition().toPoint() - self._press_position
            window = self.window()
            width = max(window.minimumWidth(), self._start_size.width() + delta.x())
            height = max(window.minimumHeight(), self._start_size.height() + delta.y())
            window.resize(width, height)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        self._press_position = None
        self._start_size = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(226, 232, 240, 150), 1.4))
        for offset in (7, 12, 17):
            painter.drawLine(
                self.width() - offset,
                self.height() - 2,
                self.width() - 2,
                self.height() - offset,
            )
        super().paintEvent(event)
