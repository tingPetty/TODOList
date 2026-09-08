from __future__ import annotations

import pyqtgraph as pg

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDateEdit, QDialog, QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from ...services.statistics_service import StatisticsService
from ..formatters import format_duration
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

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("▥ 任务统计")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        subtitle = QLabel("最近 30 天完成任务趋势")
        subtitle.setObjectName("MutedText")
        root.addWidget(subtitle)

        chart_card = SurfaceCard()
        chart_title = QLabel("完成趋势")
        chart_title.setObjectName("SectionTitle")
        chart_card.body.addWidget(chart_title)
        self.plot = pg.PlotWidget()
        self.plot.setBackground((0, 0, 0, 0))
        self.plot.showGrid(x=True, y=True, alpha=0.14)
        # The plot area is light, so use a dark, shared color for both axis
        # labels and axis lines instead of the page's light-on-dark text.
        axis_text_color = "#465a73"
        axis_line_color = "#344861"
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
        self.date_query.setDisplayFormat("yyyy-MM-dd")
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
        detail_title = QLabel("当日完成明细")
        detail_title.setObjectName("SectionTitle")
        detail_card.body.addWidget(detail_title)
        self.detail_list = QListWidget()
        self.detail_list.setObjectName("RecordList")
        detail_card.body.addWidget(self.detail_list, 1)
        root.addWidget(detail_card, 1)

        self._render_curve()
        self._refresh_day_details()

    def _render_curve(self) -> None:
        date_keys, values = self.statistics_service.completion_curve()
        x_values = list(range(len(date_keys)))
        self.plot.clear()
        self.plot.plot(
            x_values,
            values,
            pen=pg.mkPen(color="#ffd480", width=3),
            symbol="o",
            symbolSize=7,
            symbolBrush=pg.mkBrush("#ff9aa2"),
            symbolPen=pg.mkPen("#fff1f2", width=1),
            fillLevel=0,
            brush=pg.mkBrush(255, 212, 128, 55),
        )
        ticks = [(index, key[5:]) for index, key in enumerate(date_keys) if index % 5 == 0]
        self.plot.getAxis("bottom").setTicks([ticks])
        self.plot.setYRange(0, max(1, max(values) + 1), padding=0.05)

    def _refresh_day_details(self) -> None:
        key = self.date_query.date().toString("yyyy-MM-dd")
        completed = self.statistics_service.completed_on(key)
        self.day_summary.setText(f"{key} 已完成 {len(completed)} 项")
        self.detail_list.clear()
        if not completed:
            self.detail_list.addItem("这一天还没有完成任务")
            return
        for task in completed:
            prefix = "❗ " if task.important else ""
            self.detail_list.addItem(f"{prefix}{task.text}")
