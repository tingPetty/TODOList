from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QToolButton, QWidget

from ..styles.metrics import TAB_HEIGHT


class TabBar(QWidget):
    currentChanged = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(TAB_HEIGHT)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: list[QToolButton] = []
        for index, title in enumerate(("✓  Todo", "◷  专注")):
            button = QToolButton()
            button.setObjectName("TabButton")
            button.setText(title)
            button.setCheckable(True)
            button.setToolTip(f"切换到{title.split()[-1]}页面")
            button.setAccessibleName(f"{title.split()[-1]}页面")
            button.clicked.connect(lambda _checked=False, i=index: self._select(i))
            self.group.addButton(button, index)
            self.buttons.append(button)
            layout.addWidget(button, 1)

        self.setCurrentIndex(0)

    def _select(self, index: int) -> None:
        self.setCurrentIndex(index)
        self.currentChanged.emit(index)

    def setCurrentIndex(self, index: int) -> None:
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)

    def currentIndex(self) -> int:
        button = self.group.checkedId()
        return 0 if button < 0 else button
