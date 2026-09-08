from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QToolButton

from ..styles.metrics import ICON_BUTTON_SIZE


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
        self.setText(symbol)
        self.setToolTip(tooltip)
        self.setAccessibleName(accessible_name or tooltip)
        self.setObjectName(
            "DangerButton" if dangerous else
            "PrimaryButton" if primary else
            "StopButton" if stop else "IconButton"
        )
        self.setFixedSize(QSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE))
