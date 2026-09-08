from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget


class SectionHeader(QWidget):
    """Shared title row used by task groups, cards, and history sections."""

    def __init__(
        self,
        text: str,
        *,
        action_text: str | None = None,
        action_tooltip: str | None = None,
        on_action: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(8)
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
        layout.addStretch(1)
        if action_text is not None and on_action is not None:
            button = QPushButton(action_text)
            button.setObjectName("GroupToggleButton")
            if action_tooltip:
                button.setToolTip(action_tooltip)
            button.setAccessibleName(action_tooltip or action_text)
            button.clicked.connect(on_action)
            layout.addWidget(button)
