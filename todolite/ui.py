from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QInputDialog,
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
    color: rgba(148, 163, 184, 210);
    font-size: 12px;
    font-weight: 700;
    padding: 4px 2px 0 2px;
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
    def __init__(self, text: str) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 2)
        label = QLabel(text)
        label.setObjectName("GroupTitle")
        layout.addWidget(label)


class TaskRow(QWidget):
    def __init__(self, task: Task, on_toggle, on_delete, on_edit) -> None:
        super().__init__()
        self.task_id = task.id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.checkbox = QCheckBox(task.text)
        self.checkbox.setChecked(task.completed)
        self._apply_completed_style(task.completed)
        self.checkbox.toggled.connect(lambda checked: on_toggle(self.task_id, checked))

        delete_btn = QPushButton("删")
        delete_btn.setObjectName("DeleteBtn")
        delete_btn.setFixedWidth(28)
        delete_btn.clicked.connect(lambda: on_delete(self.task_id))

        self.checkbox.mouseDoubleClickEvent = lambda event: on_edit(self.task_id)

        layout.addWidget(self.checkbox, 1)
        layout.addWidget(delete_btn, 0)

    def _apply_completed_style(self, completed: bool) -> None:
        font = self.checkbox.font()
        font.setStrikeOut(completed)
        self.checkbox.setFont(font)
        if completed:
            self.checkbox.setStyleSheet("color: rgba(203, 213, 225, 140);")
        else:
            self.checkbox.setStyleSheet("color: #e2e8f0;")


class TodoWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.task_store = TaskStore()
        self.settings_store = SettingsStore()
        self.tasks = self.task_store.load()
        self.settings = self.settings_store.load()
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

        self.task_list = TaskListWidget()
        self.task_list.setObjectName("TaskList")
        self.task_list.reordered.connect(self._on_tasks_reordered)

        tip = QLabel("双击任务可编辑；未完成任务可拖拽排序")
        tip.setStyleSheet("color: rgba(226, 232, 240, 150); font-size: 12px;")

        card_layout.addLayout(header)
        card_layout.addWidget(self.input_box)
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
        return task.created_at[:10]

    def _date_label(self, key: str) -> str:
        if key == today_key():
            return "今天"
        return key

    def _sort_tasks_for_display(self) -> dict[str, list[Task]]:
        grouped: dict[str, list[Task]] = defaultdict(list)
        for task in self.tasks:
            grouped[self._date_key(task)].append(task)

        for key in grouped:
            grouped[key].sort(key=lambda t: (t.completed, t.order, t.created_at, t.id))

        return dict(sorted(grouped.items(), key=lambda kv: kv[0], reverse=True))

    def _render_tasks(self) -> None:
        self.task_list.clear()

        grouped = self._sort_tasks_for_display()
        for date_key, tasks in grouped.items():
            header_item = QListWidgetItem(self.task_list)
            header_item.setData(ITEM_TYPE_ROLE, "header")
            header_item.setFlags(Qt.ItemIsEnabled)
            header = GroupHeaderRow(self._date_label(date_key))
            header_item.setSizeHint(header.sizeHint())
            self.task_list.addItem(header_item)
            self.task_list.setItemWidget(header_item, header)

            for task in tasks:
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
        for task in sorted(self.tasks, key=lambda t: (self._date_key(t), t.completed, t.order, t.created_at, t.id)):
            if task.completed:
                updated.append(task)
                continue
            key = self._date_key(task)
            updated.append(replace(task, order=counters[key]))
            counters[key] += 1
        self.tasks = updated

    def _add_task(self) -> None:
        text = self.input_box.text().strip()
        if not text:
            return

        key = today_key()
        self.tasks.append(Task.create(text, order=self._next_order_for_date(key)))
        self.input_box.clear()
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

        text, ok = QInputDialog.getText(self, "编辑任务", "任务内容", text=task.text)
        if not ok:
            return

        new_text = text.strip()
        if not new_text:
            self._delete_task(task_id)
            return

        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks[i] = replace(t, text=new_text)
                break
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
