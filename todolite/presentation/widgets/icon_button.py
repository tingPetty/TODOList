from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolButton

from ..styles.metrics import ICON_BUTTON_SIZE
from ..styles.icons import ui_icon

SYMBOLS = {"⋯": "more", "×": "close", "▥": "chart", "▤": "history", "▶": "play", "Ⅱ": "pause", "■": "stop", "+": "plus"}


class IconButton(QToolButton):
    """A consistent symbol button with tooltip and accessible name."""

    def __init__(
        self,
        symbol: str,
        tooltip: str,
        accessible_name: str | None = None,
        *,
        dangerous: bool = False,
        primary: bool = False,
        stop: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._light_icon = primary
        self.set_symbol("trash" if dangerous and "删除" in tooltip else symbol)
        self.setToolTip(tooltip)
        self.setAccessibleName(accessible_name or tooltip)
        self.setObjectName(
            "DangerButton" if dangerous else
            "PrimaryButton" if primary else
            "StopButton" if stop else "IconButton"
        )
        self.setFixedSize(QSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE))
        self.setIconSize(QSize(18, 18))
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)

    def set_symbol(self, symbol: str) -> None:
        self.setIcon(ui_icon(SYMBOLS.get(symbol, symbol), light=self._light_icon))

    def set_label(self, text: str, width: int = 100) -> None:
        self.setText(text)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setFixedSize(width, 36)
