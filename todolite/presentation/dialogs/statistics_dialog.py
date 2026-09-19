from __future__ import annotations

import pyqtgraph as pg

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDateEdit, QDialog, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout

from ...services.statistics_service import StatisticsService
from ..styles.theme import COLORS
from ..styles.controls import style_date_picker
from ..widgets.empty_state import EmptyState
from ..widgets.surface_card import SurfaceCard


class StatisticsDialog(QDialog):
    def __init__(self, parent, statistics_service: StatisticsService) -> None:
        super().__init__(parent)
        self.setObjectName("LightDialog")
        self.statistics_service = statistics_service
        self.setWindowTitle("任务统计")
        self.setModal(True)
        self.resize(550, 510)
        self.setMinimumSize(460, 450)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("任务统计")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        subtitle = QLabel("近 30 天 · 按任务日期统计已完成项")
        subtitle.setObjectName("MutedText")
        root.addWidget(subtitle)

        chart_card = SurfaceCard()
        chart_title = QLabel("完成趋势")
        chart_title.setObjectName("SectionTitle")
        chart_header = QHBoxLayout()
        chart_header.addWidget(chart_title, 1)
        reset = QPushButton("重置视图")
        reset.setObjectName("GroupToggleButton")
        reset.clicked.connect(self._reset_view)
        chart_header.addWidget(reset)
        chart_card.body.addLayout(chart_header)
        self.plot = pg.PlotWidget()
        self.plot.setBackground(COLORS["paper"])
        self.plot.showGrid(x=False, y=True, alpha=0.12)
        self.plot.setMenuEnabled(False)
        self.plot.getPlotItem().hideButtons()
        # The plot area is light, so use a dark, shared color for both axis
        # labels and axis lines instead of the page's light-on-dark text.
        axis_text_color = COLORS["muted"]
        axis_line_color = COLORS["outline"]
        self.plot.getAxis("left").setTextPen(axis_text_color)
        self.plot.getAxis("bottom").setTextPen(axis_text_color)
        self.plot.getAxis("left").setPen(axis_line_color)
        self.plot.getAxis("bottom").setPen(axis_line_color)
        auto_button = getattr(self.plot.getPlotItem(), "autoBtn", None)
        if auto_button is not None:
            auto_button.setToolTip("自动缩放图表")
        chart_card.body.addWidget(self.plot, 1)
        root.addWidget(chart_card, 1)

        query_row = QHBoxLayout()
        query_row.addWidget(QLabel("查询日期"))
        self.date_query = QDateEdit()
        self.date_query.setCalendarPopup(True)
        style_date_picker(self.date_query)
        self.date_query.setDisplayFormat("yyyy-MM-dd")
        self.date_query.setFixedWidth(145)
        today = self.statistics_service.clock.today().isoformat()
        self.date_query.setDate(QDate.fromString(today, "yyyy-MM-dd"))
        self.date_query.dateChanged.connect(self._refresh_day_details)
        query_row.addWidget(self.date_query)
        query_row.addStretch(1)
        root.addLayout(query_row)

        self.day_summary = QLabel("")
        self.day_summary.setObjectName("SectionTitle")
        root.addWidget(self.day_summary)

        detail_card = SurfaceCard()
        detail_title = QLabel("已完成清单")
        detail_title.setObjectName("SectionTitle")
        detail_card.body.addWidget(detail_title)
        self.detail_list = QListWidget()
        self.detail_list.setObjectName("RecordList")
        self.detail_list.setWordWrap(True)
        detail_card.body.addWidget(self.detail_list, 1)
        self.empty_state = EmptyState("这个任务日期下还没有已完成项")
        detail_card.body.addWidget(self.empty_state, 1)
        root.addWidget(detail_card, 1)

        self._render_curve()
        self._refresh_day_details()

    def _render_curve(self) -> None:
        date_keys, values = self.statistics_service.completion_curve()
        self.date_keys, self.values = date_keys, values
        x_values = list(range(len(date_keys)))
        self.plot.clear()
        self.plot.plot(
            x_values,
            values,
            pen=pg.mkPen(color=COLORS["primary"], width=2),
            symbol="o",
            symbolSize=6,
            symbolBrush=pg.mkBrush(COLORS["primary"]),
            symbolPen=pg.mkPen(COLORS["paper"], width=1),
            fillLevel=0,
            brush=pg.mkBrush(187, 215, 140, 65),
        )
        ticks = [(index, key[5:]) for index, key in enumerate(date_keys) if index % 5 == 0]
        self.plot.getAxis("bottom").setTicks([ticks])
        peak = max(1, max(values))
        step = max(1, (peak + 4) // 5)
        self.plot.getAxis("left").setTicks([[(n, str(n)) for n in range(0, peak + step + 1, step)]])
        self.selected_day = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(COLORS["outline"], width=1, style=Qt.DashLine))
        self.plot.addItem(self.selected_day)
        self._reset_view()

    def _reset_view(self) -> None:
        self.plot.setXRange(0, max(1, len(self.date_keys) - 1), padding=0.02)
        self.plot.setYRange(0, max(1, max(self.values) + 1), padding=0.02)

    def _refresh_day_details(self) -> None:
        key = self.date_query.date().toString("yyyy-MM-dd")
        completed = self.statistics_service.completed_on(key)
        self.day_summary.setText(f"{key} 的任务 · 已完成 {len(completed)} 项")
        self.selected_day.setVisible(key in self.date_keys)
        if key in self.date_keys:
            self.selected_day.setValue(self.date_keys.index(key))
        self.detail_list.clear()
        self.detail_list.setVisible(bool(completed))
        self.empty_state.setVisible(not completed)
        if not completed:
            return
        for task in completed:
            prefix = "★ " if task.important else ""
            self.detail_list.addItem(f"{prefix}{task.text}")
