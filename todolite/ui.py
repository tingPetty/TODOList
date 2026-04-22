from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import pyqtgraph as pg

from PySide6.QtCore import QDate, QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import autostart
from .paths import today_key
from .settings_store import SettingsStore
from .storage import Task, TaskStore


ITEM_TYPE_ROLE = Qt.UserRole + 1
TASK_ID_ROLE = Qt.UserRole + 2
TASK_DATE_ROLE = Qt.UserRole + 3
TASK_COMPLETED_ROLE = Qt.UserRole + 4


WINDOW_CSS = """
QWidget#TodoWindow {
    background: transparent;
}
QFrame#Card {
    background: rgba(71, 85, 105, 138);
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 16px;
}
QLabel#Title {
    color: #e5e7eb;
    font-size: 18px;
    font-weight: 700;
}
QLabel#GroupTitle {
    color: #334155;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 2px 0 2px;
}
QPushButton#GroupToggleBtn {
    color: rgba(226, 232, 240, 210);
    border: none;
    border-radius: 7px;
    padding: 2px 8px;
    font-size: 11px;
    background: rgba(30, 41, 59, 80);
}
QPushButton#GroupToggleBtn:hover {
    background: rgba(51, 65, 85, 130);
}
QLineEdit#Input {
    background: rgba(255, 255, 255, 28);
    border: 1px solid rgba(255, 255, 255, 58);
    border-radius: 10px;
    color: #f8fafc;
    padding: 8px 10px;
    font-size: 14px;
}
QLineEdit#Input:focus {
    border: 1px solid rgba(226, 232, 240, 120);
    background: rgba(255, 255, 255, 34);
}
QDateEdit#DatePicker {
    background: rgba(255, 255, 255, 28);
    border: 1px solid rgba(255, 255, 255, 58);
    border-radius: 10px;
    color: #f8fafc;
    padding: 6px 8px;
    font-size: 13px;
}
QDateEdit#DatePicker:focus {
    border: 1px solid rgba(226, 232, 240, 120);
}
QListWidget#TaskList {
    background: transparent;
    border: none;
    outline: none;
}
QCheckBox {
    color: #e2e8f0;
    font-size: 14px;
    spacing: 10px;
}
QCheckBox#ImportantSwitch {
    color: #f8fafc;
    font-size: 13px;
    font-weight: 600;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid rgba(226, 232, 240, 140);
    border-radius: 4px;
    background: rgba(15, 23, 42, 120);
}
QCheckBox::indicator:checked {
    background: rgba(74, 222, 128, 190);
    border: 1px solid rgba(134, 239, 172, 220);
}
QPushButton#DeleteBtn {
    color: rgba(248, 250, 252, 180);
    border: none;
    border-radius: 8px;
    padding: 2px 6px;
    background: rgba(248, 113, 113, 28);
}
QPushButton#DeleteBtn:hover {
    color: rgba(255, 255, 255, 230);
    background: rgba(248, 113, 113, 64);
}
QToolButton#MenuBtn {
    color: #e2e8f0;
    border: none;
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 8px;
}
QToolButton#MenuBtn:hover {
    background: rgba(255, 255, 255, 25);
}
QLabel#TaskText {
    color: #e2e8f0;
    font-size: 14px;
}
"""


class TaskListWidget(QListWidget):
    reordered = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, event):  # noqa: N802
        super().dropEvent(event)
        self.reordered.emit()


class GroupHeaderRow(QWidget):
    def __init__(self, text: str, completed_count: int, collapsed: bool, on_toggle_completed) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 2)
        layout.setSpacing(8)
        label = QLabel(text)
        label.setObjectName("GroupTitle")
        layout.addWidget(label)
        layout.addStretch(1)

        if completed_count > 0:
            btn = QPushButton(
                f"展开已完成 {completed_count}" if collapsed else f"收起已完成 {completed_count}"
            )
            btn.setObjectName("GroupToggleBtn")
            btn.clicked.connect(on_toggle_completed)
            layout.addWidget(btn)


class TaskTextLabel(QLabel):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):  # noqa: N802
        self.doubleClicked.emit()
        event.accept()


class TaskRow(QWidget):
    def __init__(self, task: Task, on_toggle, on_delete, on_edit) -> None:
        super().__init__()
        self.task_id = task.id
        self.important = task.important

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.completed)
        self.checkbox.toggled.connect(lambda checked: on_toggle(self.task_id, checked))
        self.checkbox.setFixedWidth(18)

        self.text_label = TaskTextLabel(self._display_text(task))
        self.text_label.setObjectName("TaskText")
        self.text_label.doubleClicked.connect(lambda: on_edit(self.task_id))
        self._apply_completed_style(task.completed)

        delete_btn = QPushButton("删")
        delete_btn.setObjectName("DeleteBtn")
        delete_btn.setFixedWidth(28)
        delete_btn.clicked.connect(lambda: on_delete(self.task_id))

        layout.addWidget(self.checkbox, 0)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(delete_btn, 0)

    def _display_text(self, task: Task) -> str:
        return f"❗ {task.text}" if task.important else task.text

    def _apply_completed_style(self, completed: bool) -> None:
        font = self.text_label.font()
        font.setStrikeOut(completed)
        font.setBold(self.important)
        self.text_label.setFont(font)
        if completed:
            self.text_label.setStyleSheet("color: rgba(203, 213, 225, 140);")
        else:
            self.text_label.setStyleSheet("color: #e2e8f0;")


class TaskEditDialog(QDialog):
    def __init__(self, parent: QWidget, task: Task) -> None:
        super().__init__(parent)
        self.setWindowTitle("编辑任务")
        self.setModal(True)
        self.resize(320, 150)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.text_input = QLineEdit(task.text)
        self.text_input.setPlaceholderText("任务内容")

        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        date = QDate.fromString(task.task_date, "yyyy-MM-dd")
        if not date.isValid():
            date = QDate.currentDate()
        self.date_edit.setDate(date)

        self.important_check = QCheckBox("重要任务")
        self.important_check.setChecked(task.important)

        form.addRow("内容", self.text_input)
        form.addRow("日期", self.date_edit)
        form.addRow("标记", self.important_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root.addLayout(form)
        root.addWidget(buttons)

    def accept(self) -> None:
        if not self.text_input.text().strip():
            QMessageBox.warning(self, "编辑任务", "任务内容不能为空")
            return
        super().accept()

    def values(self) -> tuple[str, str, bool]:
        return (
            self.text_input.text().strip(),
            self.date_edit.date().toString("yyyy-MM-dd"),
            self.important_check.isChecked(),
        )


class TaskStatsDialog(QDialog):
    def __init__(self, parent: QWidget, tasks: list[Task]) -> None:
        super().__init__(parent)
        self.tasks = tasks
        self._drag_offset: QPoint | None = None
        self._dragging = False
        self.setModal(True)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(540, 460)
        self.setObjectName("StatsDialog")
        self.setStyleSheet(
            "QDialog#StatsDialog {"
            "  background: transparent;"
            "}"
            "QFrame#StatsSurface {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "    stop:0 rgba(79, 101, 128, 232),"
            "    stop:0.55 rgba(68, 89, 117, 235),"
            "    stop:1 rgba(63, 84, 108, 238));"
            "  border: none;"
            "  border-radius: 18px;"
            "}"
            "QLabel { color: #e8eef7; font-size: 13px; }"
            "QLabel#StatsTitle { color: #f8fbff; font-size: 28px; font-weight: 800; letter-spacing: 1px; }"
            "QLabel#StatsSubtitle { color: rgba(235, 245, 255, 185); font-size: 12px; }"
            "QLabel#DaySummary { color: #f8fbff; font-size: 14px; font-weight: 700; }"
            "QFrame#StatsCard {"
            "  background: rgba(23, 36, 54, 110);"
            "  border: 1px solid rgba(255,255,255,32);"
            "  border-radius: 14px;"
            "}"
            "QListWidget {"
            "  background: rgba(22, 34, 52, 120);"
            "  color: #ebf2fd;"
            "  border: 1px solid rgba(255,255,255,28);"
            "  border-radius: 12px;"
            "  padding: 6px;"
            "}"
            "QDateEdit {"
            "  background: rgba(255,255,255,22);"
            "  color: #eef5ff;"
            "  border: 1px solid rgba(255,255,255,60);"
            "  border-radius: 10px;"
            "  padding: 5px 8px;"
            "  font-size: 13px;"
            "}"
            "QPushButton#StatsTopCloseBtn {"
            "  background: rgba(239, 68, 68, 230);"
            "  color: #fff1f2;"
            "  border: 1px solid rgba(255,255,255,75);"
            "  border-radius: 9px;"
            "  min-width: 26px;"
            "  max-width: 26px;"
            "  min-height: 26px;"
            "  max-height: 26px;"
            "  font-size: 14px;"
            "  font-weight: 700;"
            "}"
            "QPushButton#StatsTopCloseBtn:hover { background: rgba(220, 38, 38, 240); }"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("StatsSurface")
        root.addWidget(surface)

        body = QVBoxLayout(surface)
        body.setContentsMargins(14, 14, 14, 14)
        body.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        top_row.addStretch(1)
        top_close_btn = QPushButton("X")
        top_close_btn.setObjectName("StatsTopCloseBtn")
        top_close_btn.clicked.connect(self.accept)
        top_row.addWidget(top_close_btn, 0, Qt.AlignRight)
        body.addLayout(top_row)

        title = QLabel("任务统计")
        title.setObjectName("StatsTitle")
        body.addWidget(title)

        subtitle = QLabel("最近30天完成任务曲线")
        subtitle.setObjectName("StatsSubtitle")
        body.addWidget(subtitle)

        chart_card = QFrame()
        chart_card.setObjectName("StatsCard")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        chart_layout.setSpacing(8)

        chart_caption = QLabel("完成趋势")
        chart_caption.setStyleSheet("color: rgba(242, 248, 255, 220); font-size: 13px; font-weight: 700;")
        chart_layout.addWidget(chart_caption)

        self.plot = pg.PlotWidget()
        self.plot.setBackground((0, 0, 0, 0))
        self.plot.showGrid(x=True, y=True, alpha=0.14)
        self.plot.getAxis("left").setTextPen("#d7e5f7")
        self.plot.getAxis("bottom").setTextPen("#d7e5f7")
        self.plot.getAxis("left").setPen("#8ca4c2")
        self.plot.getAxis("bottom").setPen("#8ca4c2")
        chart_layout.addWidget(self.plot, 1)

        body.addWidget(chart_card, 1)

        query_row = QHBoxLayout()
        query_row.setSpacing(8)
        query_row.addWidget(QLabel("查询日期"))

        self.date_query = QDateEdit()
        self.date_query.setCalendarPopup(True)
        self.date_query.setDisplayFormat("yyyy-MM-dd")
        self.date_query.setDate(QDate.currentDate())
        self.date_query.dateChanged.connect(self._refresh_day_details)
        query_row.addWidget(self.date_query)
        query_row.addStretch(1)
        body.addLayout(query_row)

        self.day_summary = QLabel("")
        self.day_summary.setObjectName("DaySummary")
        body.addWidget(self.day_summary)

        detail_card = QFrame()
        detail_card.setObjectName("StatsCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(8, 8, 8, 8)
        detail_layout.setSpacing(6)

        detail_title = QLabel("当日完成明细")
        detail_title.setStyleSheet("color: rgba(242, 248, 255, 220); font-size: 13px; font-weight: 700;")
        detail_layout.addWidget(detail_title)

        self.detail_list = QListWidget()
        detail_layout.addWidget(self.detail_list, 1)
        body.addWidget(detail_card, 1)

        self._render_curve()
        self._refresh_day_details()

    def _is_top_drag_zone(self, local_pos: QPoint) -> bool:
        if local_pos.y() > 48:
            return False
        if local_pos.x() > self.width() - 56:
            return False
        return True

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.LeftButton and self._is_top_drag_zone(event.pos()):
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._dragging and self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        self._dragging = False
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def _render_curve(self) -> None:
        today = beijing_today_date()
        start = today - timedelta(days=29)
        date_keys = [(start + timedelta(days=i)).isoformat() for i in range(30)]

        completed_count: dict[str, int] = defaultdict(int)
        for task in self.tasks:
            if task.completed:
                completed_count[task.task_date] += 1

        x_vals = list(range(30))
        y_vals = [completed_count.get(k, 0) for k in date_keys]

        self.plot.clear()
        curve_pen = pg.mkPen(color="#ffd480", width=3)
        fill_brush = pg.mkBrush(255, 212, 128, 55)
        dot_brush = pg.mkBrush("#ff9aa2")
        self.plot.plot(
            x_vals,
            y_vals,
            pen=curve_pen,
            symbol="o",
            symbolSize=7,
            symbolBrush=dot_brush,
            symbolPen=pg.mkPen("#fff1f2", width=1),
            fillLevel=0,
            brush=fill_brush,
        )

        # Keep axis labels readable by showing every 5 days.
        ticks = [(i, date_keys[i][5:]) for i in range(0, 30, 5)]
        self.plot.getAxis("bottom").setTicks([ticks])
        self.plot.setYRange(0, max(1, max(y_vals) + 1), padding=0.05)

    def _refresh_day_details(self) -> None:
        key = self.date_query.date().toString("yyyy-MM-dd")
        done = [t for t in self.tasks if t.completed and t.task_date == key]

        self.day_summary.setText(f"{key} 已完成 {len(done)} 项")
        self.detail_list.clear()
        if not done:
            self.detail_list.addItem("今天先休息一下，明天继续加油")
            return

        for task in sorted(done, key=lambda t: (t.order, t.created_at, t.id)):
            prefix = "❗ " if task.important else ""
            self.detail_list.addItem(f"{prefix}{task.text}")


BJ_TZ = timezone(timedelta(hours=8))


def beijing_today_date() -> date:
    return datetime.now(BJ_TZ).date()


class TodoWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.task_store = TaskStore()
        self.settings_store = SettingsStore()
        self.tasks = self.task_store.load()
        self.settings = self.settings_store.load()
        self.collapsed_completed_dates: dict[str, bool] = dict(
            self.settings.get("collapsed_completed_dates", {})
        )
        self.drag_start: QPoint | None = None

        self.setObjectName("TodoWindow")
        self.setWindowTitle("Desktop Todo Lite")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(380, 540)

        self._build_ui()
        self._load_state()
        self._cleanup_completed_before_or_on(self._cleanup_cutoff_date_key())
        self._render_tasks()

    def _build_ui(self) -> None:
        self.setStyleSheet(WINDOW_CSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("Card")
        root.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 14)
        card_layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Day Todo")
        title.setObjectName("Title")

        menu_btn = QToolButton()
        menu_btn.setObjectName("MenuBtn")
        menu_btn.setText("...")
        menu_btn.setPopupMode(QToolButton.InstantPopup)
        menu_btn.setMenu(self._build_menu())

        stats_btn = QToolButton()
        stats_btn.setObjectName("MenuBtn")
        stats_btn.setText("统计")
        stats_btn.clicked.connect(self._show_task_stats)

        header.addWidget(title, 1)
        header.addWidget(stats_btn)
        header.addWidget(menu_btn)

        self.input_box = QLineEdit()
        self.input_box.setObjectName("Input")
        self.input_box.setPlaceholderText("输入任务后按回车添加")
        self.input_box.returnPressed.connect(self._add_task)

        self.date_picker = QDateEdit()
        self.date_picker.setObjectName("DatePicker")
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setFixedWidth(118)

        self.important_switch = QCheckBox("重要")
        self.important_switch.setObjectName("ImportantSwitch")

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(8)
        input_row.addWidget(self.input_box, 1)
        input_row.addWidget(self.date_picker, 0)
        input_row.addWidget(self.important_switch, 0)

        self.task_list = TaskListWidget()
        self.task_list.setObjectName("TaskList")
        self.task_list.reordered.connect(self._on_tasks_reordered)

        tip = QLabel("双击文本可编辑；仅点左侧方框完成；未完成任务可拖拽")
        tip.setStyleSheet("color: rgba(226, 232, 240, 150); font-size: 12px;")

        card_layout.addLayout(header)
        card_layout.addLayout(input_row)
        card_layout.addWidget(self.task_list, 1)
        card_layout.addWidget(tip)

    def _build_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: rgba(17, 24, 39, 235); color: #e2e8f0; border: 1px solid rgba(255,255,255,35); }"
            "QMenu::item:selected { background: rgba(148, 163, 184, 70); }"
        )

        self.action_on_top = QAction("窗口置顶", self, checkable=True)
        self.action_on_top.toggled.connect(self._toggle_always_on_top)

        self.action_autostart = QAction("开机自启", self, checkable=True)
        self.action_autostart.toggled.connect(self._toggle_autostart)

        stats_action = QAction("任务统计", self)
        stats_action.triggered.connect(self._show_task_stats)

        close_action = QAction("退出", self)
        close_action.triggered.connect(self.close)

        menu.addAction(self.action_on_top)
        menu.addAction(self.action_autostart)
        menu.addAction(stats_action)
        menu.addSeparator()
        menu.addAction(close_action)
        return menu

    def _cleanup_cutoff_date_key(self) -> str:
        return (beijing_today_date() - timedelta(days=2)).isoformat()

    def _cleanup_completed_before_or_on(self, cutoff_date_key: str) -> None:
        kept = [
            task
            for task in self.tasks
            if not (task.completed and task.task_date <= cutoff_date_key)
        ]
        if len(kept) == len(self.tasks):
            return

        self.tasks = kept
        self._reindex_active_order()
        self.task_store.save(self.tasks)

    def _load_state(self) -> None:
        self.action_on_top.setChecked(self.settings.get("always_on_top", False))

        startup_enabled = autostart.is_enabled()
        desired = self.settings.get("start_with_windows", False)
        self.action_autostart.setChecked(startup_enabled or desired)

        self._apply_window_flags(self.action_on_top.isChecked())

    def _apply_window_flags(self, always_on_top: bool) -> None:
        pos = self.pos()
        flags = Qt.FramelessWindowHint | Qt.Window
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.move(pos)

    def _date_key(self, task: Task) -> str:
        return task.task_date

    def _date_label(self, key: str) -> str:
        if key == today_key():
            return "今天"
        return key

    def _sort_tasks_for_display(self) -> dict[str, list[Task]]:
        grouped: dict[str, list[Task]] = defaultdict(list)
        for task in self.tasks:
            grouped[self._date_key(task)].append(task)

        for key in grouped:
            grouped[key].sort(key=lambda t: (t.completed, not t.important, t.order, t.created_at, t.id))

        return dict(sorted(grouped.items(), key=lambda kv: kv[0], reverse=True))

    def _render_tasks(self) -> None:
        self.task_list.clear()

        grouped = self._sort_tasks_for_display()
        for date_key, tasks in grouped.items():
            active_tasks = [t for t in tasks if not t.completed]
            completed_tasks = [t for t in tasks if t.completed]
            collapsed = self.collapsed_completed_dates.get(date_key, False)

            header_item = QListWidgetItem(self.task_list)
            header_item.setData(ITEM_TYPE_ROLE, "header")
            header_item.setData(TASK_DATE_ROLE, date_key)
            header_item.setFlags(Qt.ItemIsEnabled)
            header = GroupHeaderRow(
                self._date_label(date_key),
                completed_count=len(completed_tasks),
                collapsed=collapsed,
                on_toggle_completed=lambda _, dk=date_key: self._toggle_completed_group(dk),
            )
            header_item.setSizeHint(header.sizeHint())
            self.task_list.addItem(header_item)
            self.task_list.setItemWidget(header_item, header)

            visible_tasks = active_tasks if collapsed else tasks
            for task in visible_tasks:
                item = QListWidgetItem(self.task_list)
                item.setData(ITEM_TYPE_ROLE, "task")
                item.setData(TASK_ID_ROLE, task.id)
                item.setData(TASK_DATE_ROLE, date_key)
                item.setData(TASK_COMPLETED_ROLE, task.completed)

                flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
                if not task.completed:
                    flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
                item.setFlags(flags)

                row = TaskRow(task, self._toggle_task, self._delete_task, self._edit_task)
                item.setSizeHint(row.sizeHint())
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, row)

    def _next_order_for_date(self, date_key: str) -> int:
        active = [t.order for t in self.tasks if self._date_key(t) == date_key and not t.completed]
        if not active:
            return 0
        return max(active) + 1

    def _reindex_active_order(self) -> None:
        counters: dict[str, int] = defaultdict(int)
        updated: list[Task] = []
        for task in sorted(
            self.tasks,
            key=lambda t: (self._date_key(t), t.completed, not t.important, t.order, t.created_at, t.id),
        ):
            if task.completed:
                updated.append(task)
                continue
            key = self._date_key(task)
            updated.append(replace(task, order=counters[key]))
            counters[key] += 1
        self.tasks = updated

    def _toggle_completed_group(self, date_key: str) -> None:
        current = self.collapsed_completed_dates.get(date_key, False)
        next_state = not current
        if next_state:
            self.collapsed_completed_dates[date_key] = True
        else:
            self.collapsed_completed_dates.pop(date_key, None)

        self.settings["collapsed_completed_dates"] = dict(self.collapsed_completed_dates)
        self.settings_store.save(self.settings)
        self._render_tasks()

    def _add_task(self) -> None:
        text = self.input_box.text().strip()
        if not text:
            return

        key = self.date_picker.date().toString("yyyy-MM-dd")
        important = self.important_switch.isChecked()
        self.tasks.append(Task.create(text, order=self._next_order_for_date(key), task_date=key, important=important))
        self.input_box.clear()
        self.important_switch.setChecked(False)
        self._save_tasks_and_refresh()

    def _toggle_task(self, task_id: str, completed: bool) -> None:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                task_date = self._date_key(task)
                if completed:
                    self.tasks[i] = replace(task, completed=True)
                else:
                    self.tasks[i] = replace(task, completed=False, order=self._next_order_for_date(task_date))
                break
        self._reindex_active_order()
        self._save_tasks_and_refresh()

    def _delete_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._reindex_active_order()
        self._save_tasks_and_refresh()

    def _edit_task(self, task_id: str) -> None:
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return

        dialog = TaskEditDialog(self, task)
        if dialog.exec() != QDialog.Accepted:
            return

        new_text, new_date, new_important = dialog.values()

        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                next_order = t.order
                if not t.completed and t.task_date != new_date:
                    next_order = self._next_order_for_date(new_date)
                self.tasks[i] = replace(
                    t,
                    text=new_text,
                    task_date=new_date,
                    important=new_important,
                    order=next_order,
                )
                break
        self._reindex_active_order()
        self._save_tasks_and_refresh()

    def _on_tasks_reordered(self) -> None:
        counters: dict[str, int] = defaultdict(int)
        new_orders: dict[str, int] = {}
        new_dates: dict[str, str] = {}
        current_group_date: str | None = None

        for idx in range(self.task_list.count()):
            item = self.task_list.item(idx)
            if item.data(ITEM_TYPE_ROLE) == "header":
                header_date = item.data(TASK_DATE_ROLE)
                current_group_date = str(header_date) if header_date else None
                continue

            if item.data(ITEM_TYPE_ROLE) != "task":
                continue

            if bool(item.data(TASK_COMPLETED_ROLE)):
                continue

            task_id = item.data(TASK_ID_ROLE)
            date_key = current_group_date or item.data(TASK_DATE_ROLE)
            if not task_id or not date_key:
                continue

            new_orders[str(task_id)] = counters[str(date_key)]
            new_dates[str(task_id)] = str(date_key)
            counters[str(date_key)] += 1

        changed = False
        for i, task in enumerate(self.tasks):
            if task.id not in new_orders:
                continue

            next_order = new_orders[task.id]
            next_date = new_dates.get(task.id, task.task_date)
            if task.order != next_order or task.task_date != next_date:
                self.tasks[i] = replace(task, order=next_order, task_date=next_date)
                changed = True

        if changed:
            self._save_tasks_and_refresh()

    def _show_task_stats(self) -> None:
        dialog = TaskStatsDialog(self, self.tasks)
        dialog.exec()

    def _save_tasks_and_refresh(self) -> None:
        self.task_store.save(self.tasks)
        self._render_tasks()

    def _toggle_always_on_top(self, checked: bool) -> None:
        self.settings["always_on_top"] = checked
        self.settings_store.save(self.settings)
        self._apply_window_flags(checked)

    def _toggle_autostart(self, checked: bool) -> None:
        ok, msg = autostart.set_enabled(checked)
        if not ok:
            self.action_autostart.blockSignals(True)
            self.action_autostart.setChecked(not checked)
            self.action_autostart.blockSignals(False)
            QMessageBox.warning(self, "开机自启", msg)
            return

        self.settings["start_with_windows"] = checked
        self.settings_store.save(self.settings)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self.drag_start is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_start)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        self.drag_start = None
        super().mouseReleaseEvent(event)
