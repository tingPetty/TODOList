from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

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

        header.addWidget(title, 1)
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

        close_action = QAction("退出", self)
        close_action.triggered.connect(self.close)

        menu.addAction(self.action_on_top)
        menu.addAction(self.action_autostart)
        menu.addSeparator()
        menu.addAction(close_action)
        return menu

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

        for idx in range(self.task_list.count()):
            item = self.task_list.item(idx)
            if item.data(ITEM_TYPE_ROLE) != "task":
                continue

            if bool(item.data(TASK_COMPLETED_ROLE)):
                continue

            task_id = item.data(TASK_ID_ROLE)
            date_key = item.data(TASK_DATE_ROLE)
            if not task_id or not date_key:
                continue

            new_orders[str(task_id)] = counters[str(date_key)]
            counters[str(date_key)] += 1

        changed = False
        for i, task in enumerate(self.tasks):
            if task.id in new_orders and task.order != new_orders[task.id]:
                self.tasks[i] = replace(task, order=new_orders[task.id])
                changed = True

        if changed:
            self._save_tasks_and_refresh()

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
