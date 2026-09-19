from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout

from ...services.focus_service import FocusService
from ..styles.metrics import PAGE_MARGIN
from ..widgets.empty_state import EmptyState
from ..widgets.focus_record_row import FocusRecordRow
from ..widgets.surface_card import SurfaceCard


class FocusHistoryDialog(QDialog):
    def __init__(self, parent, focus_service: FocusService) -> None:
        super().__init__(parent)
        self.focus_service = focus_service
        self.setObjectName("LightDialog")
        self.setWindowTitle("专注历史")
        self.setModal(True)
        self.resize(390, 430)
        self.setMinimumSize(360, 320)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("专注历史")
        title.setObjectName("DialogTitle")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)
        subtitle = QLabel("最近 7 个自然日 · 每一段投入都值得记录")
        subtitle.setObjectName("MutedText")
        root.addWidget(subtitle)

        self.card = SurfaceCard()
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("RecordList")
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.card.body.addWidget(self.list_widget)
        root.addWidget(self.card, 1)
        self._render()

    def _render(self) -> None:
        self.list_widget.clear()
        sessions = self.focus_service.sessions()
        if not sessions:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemIsEnabled)
            self.list_widget.addItem(item)
            empty = EmptyState("最近 7 天还没有专注记录\n结束一段专注后，会记录在这里")
            item.setSizeHint(empty.sizeHint())
            self.list_widget.setItemWidget(item, empty)
            return

        for session in sessions:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemIsEnabled)
            row = FocusRecordRow(session, self._delete_session)
            item.setSizeHint(row.sizeHint().expandedTo(row.minimumSize()))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row)

    def _delete_session(self, session_id: str) -> None:
        self.focus_service.delete_session(session_id)
        self._render()
