from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QDate, QTimer, Qt
from PySide6.QtWidgets import QDateEdit, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidgetItem, QToolButton, QVBoxLayout, QWidget
from ..styles.icons import ui_icon
from ..styles.controls import style_date_picker

from ...services.task_service import TaskService
from ..dialogs.task_edit_dialog import TaskEditDialog
from ..styles.metrics import PAGE_MARGIN, SECTION_SPACING
from ..widgets.empty_state import EmptyState
from ..widgets.icon_button import IconButton
from ..widgets.surface_card import SurfaceCard
from ..widgets.task_group_header import TaskGroupHeader
from ..widgets.task_list import (
    ITEM_TYPE_ROLE,
    TASK_COMPLETED_ROLE,
    TASK_DATE_ROLE,
    TASK_ID_ROLE,
    TaskListWidget,
)
from ..widgets.task_row import TaskRow


class TodoPage(QWidget):
    def __init__(
        self,
        task_service: TaskService,
        on_show_stats: Callable[[], None],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.task_service = task_service
        self.on_show_stats = on_show_stats
        self.setObjectName("TodoPage")
        self._build_ui()
        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(lambda: self.page_title.setText("任务清单"))
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        root.setSpacing(SECTION_SPACING)

        card = SurfaceCard()
        header = QHBoxLayout()
        title = QLabel("任务清单")
        self.page_title = title
        title.setObjectName("PageTitle")
        stats_button = IconButton("▥", "任务统计", "任务统计")
        stats_button.clicked.connect(self.on_show_stats)
        header.addWidget(title, 1)
        header.addWidget(stats_button)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("写下一件小事，回车添加…")
        self.input_box.setMinimumWidth(0)
        self.input_box.returnPressed.connect(self._add_task)

        self.date_picker = QDateEdit()
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        self.date_picker.setCalendarPopup(True)
        style_date_picker(self.date_picker)
        self.date_picker.setDate(QDate.fromString(self.task_service.clock.today().isoformat(), "yyyy-MM-dd"))
        self.date_picker.setFixedWidth(140)
        self.date_picker.setAccessibleName("任务日期")

        self.important_switch = QToolButton()
        self.important_switch.setObjectName("ImportantButton")
        self.important_switch.setText("重要")
        self.important_switch.setIcon(ui_icon("star"))
        self.important_switch.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.important_switch.setCheckable(True)
        self.important_switch.setFocusPolicy(Qt.StrongFocus)
        self.important_switch.setToolTip("标记为重要任务")
        self.important_switch.setAccessibleName("重要任务")
        self.important_switch.setFixedHeight(36)
        self.add_button = IconButton("+", "添加任务", primary=True)
        self.add_button.setFixedSize(36, 36)
        self.add_button.clicked.connect(self._add_task)
        input_row = QHBoxLayout()
        input_row.setSpacing(7)
        input_row.addWidget(self.input_box, 1)
        input_row.addWidget(self.add_button)
        options_row = QHBoxLayout()
        options_row.setSpacing(8)
        options_row.addWidget(self.date_picker)
        options_row.addWidget(self.important_switch)
        options_row.addStretch()
        self.error_label = QLabel("先写下一件小事吧")
        self.error_label.setObjectName("ErrorText")
        self.error_label.hide()
        self.input_box.textEdited.connect(lambda: self.error_label.hide())

        self.task_list = TaskListWidget()
        self.task_list.setObjectName("TaskList")
        self.task_list.setMinimumSize(0, 0)
        self.task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.task_list.reordered.connect(self._on_tasks_reordered)

        card.body.addLayout(header)
        card.body.addLayout(input_row)
        card.body.addLayout(options_row)
        card.body.addWidget(self.error_label)
        card.body.addWidget(self.task_list, 1)
        self._empty_state = EmptyState("这里还没有待办\n从一件小事开始吧")
        card.body.addWidget(self._empty_state, 1)
        root.addWidget(card, 1)

    def refresh(self) -> None:
        scroll = self.task_list.verticalScrollBar().value()
        self.task_list.clear()
        groups = self.task_service.display_groups()
        self._empty_state.setVisible(not groups)
        self.task_list.setVisible(bool(groups))
        if not groups:
            return

        for group in groups:
            date_key = group.date_key
            header_item = QListWidgetItem()
            header_item.setData(ITEM_TYPE_ROLE, "header")
            header_item.setData(TASK_DATE_ROLE, date_key)
            header_item.setFlags(Qt.ItemIsEnabled)
            self.task_list.addItem(header_item)
            header = TaskGroupHeader(
                self.task_service.date_label(date_key),
                len(group.completed_tasks),
                self.task_service.is_group_collapsed(date_key),
                lambda dk=date_key: self._toggle_completed_group(dk),
            )
            header_item.setSizeHint(header.sizeHint())
            self.task_list.setItemWidget(header_item, header)

            visible_tasks = list(group.active_tasks)
            if not self.task_service.is_group_collapsed(date_key):
                visible_tasks.extend(group.completed_tasks)
            for task in visible_tasks:
                item = QListWidgetItem()
                item.setData(ITEM_TYPE_ROLE, "task")
                item.setData(TASK_ID_ROLE, task.id)
                item.setData(TASK_DATE_ROLE, date_key)
                item.setData(TASK_COMPLETED_ROLE, task.completed)
                flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
                if not task.completed:
                    flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
                item.setFlags(flags)
                row = TaskRow(
                    task,
                    self._toggle_task,
                    self._delete_task,
                    self._edit_task,
                )
                item.setSizeHint(row.sizeHint().expandedTo(row.minimumSize()))
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, row)
        self.task_list.verticalScrollBar().setValue(scroll)

    def _toggle_completed_group(self, date_key: str) -> None:
        self.task_service.toggle_completed_group(date_key)
        self.refresh()

    def _add_task(self) -> None:
        try:
            self.task_service.add_task(
                self.input_box.text(),
                self.date_picker.date().toString("yyyy-MM-dd"),
                self.important_switch.isChecked(),
            )
        except ValueError:
            self.error_label.show()
            self.input_box.setFocus()
            return
        self.error_label.hide()
        self.input_box.clear()
        self.important_switch.setChecked(False)
        self.refresh()

    def _toggle_task(self, task_id: str, completed: bool) -> None:
        self.task_service.toggle_task(task_id, completed)
        self.refresh()
        if completed:
            self.page_title.setText("又完成一件小事")
            self.feedback_timer.start(1800)

    def _delete_task(self, task_id: str) -> None:
        self.task_service.delete_task(task_id)
        self.refresh()

    def _edit_task(self, task_id: str) -> None:
        task = next((item for item in self.task_service.tasks if item.id == task_id), None)
        if task is None:
            return
        dialog = TaskEditDialog(self, task)
        if dialog.exec() != QDialog.Accepted:
            return
        text, task_date, important = dialog.values()
        self.task_service.edit_task(task_id, text, task_date, important)
        self.refresh()

    def _on_tasks_reordered(self) -> None:
        ordered_items: list[tuple[str, str]] = []
        current_group_date: str | None = None
        for index in range(self.task_list.count()):
            item = self.task_list.item(index)
            if item.data(ITEM_TYPE_ROLE) == "header":
                current_group_date = str(item.data(TASK_DATE_ROLE))
                continue
            if item.data(ITEM_TYPE_ROLE) != "task":
                continue
            if bool(item.data(TASK_COMPLETED_ROLE)):
                continue
            task_id = item.data(TASK_ID_ROLE)
            date_key = current_group_date or item.data(TASK_DATE_ROLE)
            if task_id and date_key:
                ordered_items.append((str(task_id), str(date_key)))
        self.task_service.reorder_tasks(ordered_items)
        self.refresh()
