from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel, QSizePolicy


class ElidedLabel(QLabel):
    """Keep full plain text accessible while painting a single elided line."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setTextFormat(Qt.PlainText)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

    def minimumSizeHint(self):
        return QSize(0, self.fontMetrics().height() + 4)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())
        painter.setPen(self.palette().color(self.foregroundRole()))
        text = self.fontMetrics().elidedText(self.text(), Qt.ElideRight, self.contentsRect().width())
        painter.drawText(self.contentsRect(), self.alignment() | Qt.AlignVCenter, text)
