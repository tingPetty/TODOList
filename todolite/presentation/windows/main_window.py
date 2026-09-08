from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenu, QMessageBox, QStackedWidget, QToolButton, QVBoxLayout, QWidget

from ...app.window_controller import WindowController
from ..dialogs.statistics_dialog import StatisticsDialog
from ..pages.focus_page import FocusPage
from ..pages.todo_page import TodoPage
from ..widgets.icon_button import IconButton
from ..widgets.surface_card import SurfaceCard
from ..widgets.tab_bar import TabBar
from ..widgets.title_bar import DraggableHeader
from ..widgets.resize_grip import ResizeGrip
from ..styles.icons import app_icon
from ..styles.metrics import WINDOW_HEIGHT, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_WIDTH


class MainWindow(QWidget):
    def __init__(self, controller: WindowController, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("TodoWindow")
        self.setWindowTitle("Desktop Todo Lite")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(app_icon())
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._build_ui()
        self.resize_grip = ResizeGrip(self)
        self.resize_grip.raise_()
        self._position_resize_grip()
        self._load_state()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        shell = SurfaceCard()
        shell.body.setContentsMargins(12, 8, 12, 8)
        shell.body.setSpacing(4)
        root.addWidget(shell)

        header = DraggableHeader(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(2, 0, 2, 0)
        header_layout.setSpacing(6)
        title = QLabel("✓ Day Todo")
        title.setObjectName("AppTitle")
        title.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.menu_button = IconButton("⋯", "更多设置", "更多设置")
        self.menu_button.setMenu(self._build_menu())
        self.menu_button.setPopupMode(QToolButton.InstantPopup)
        self.close_button = IconButton("×", "退出软件", "退出软件", dangerous=True)
        self.close_button.clicked.connect(self.close)
        header_layout.addWidget(title, 1)
        header_layout.addWidget(self.menu_button)
        header_layout.addWidget(self.close_button)
        shell.body.addWidget(header)

        self.tab_bar = TabBar()
        shell.body.addWidget(self.tab_bar)

        self.page_stack = QStackedWidget()
        self.todo_page = TodoPage(
            self.controller.task_service, self._show_statistics
        )
        self.focus_page = FocusPage(
            self.controller.focus_service, self._show_focus_history
        )
        self.page_stack.addWidget(self.todo_page)
        self.page_stack.addWidget(self.focus_page)
        self.tab_bar.currentChanged.connect(self.page_stack.setCurrentIndex)
        shell.body.addWidget(self.page_stack, 1)

        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self._switch_page(0))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self._switch_page(1))

    def _position_resize_grip(self) -> None:
        if not hasattr(self, "resize_grip"):
            return
        margin = 2
        self.resize_grip.move(
            self.width() - self.resize_grip.width() - margin,
            self.height() - self.resize_grip.height() - margin,
        )

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._position_resize_grip()

    def _switch_page(self, index: int) -> None:
        self.tab_bar.setCurrentIndex(index)
        self.page_stack.setCurrentIndex(index)

    def _build_menu(self) -> QMenu:
        menu = QMenu(self)
        self.action_on_top = QAction("窗口置顶", self, checkable=True)
        self.action_on_top.toggled.connect(self._toggle_always_on_top)
        self.action_autostart = QAction("开机自启", self, checkable=True)
        self.action_autostart.toggled.connect(self._toggle_autostart)
        stats_action = QAction("任务统计", self)
        stats_action.triggered.connect(self._show_statistics)
        close_action = QAction("退出", self)
        close_action.triggered.connect(self.close)
        menu.addAction(self.action_on_top)
        menu.addAction(self.action_autostart)
        menu.addAction(stats_action)
        menu.addSeparator()
        menu.addAction(close_action)
        return menu

    def _load_state(self) -> None:
        self.action_on_top.setChecked(self.controller.settings.always_on_top)
        self.action_autostart.blockSignals(True)
        self.action_autostart.setChecked(
            self.controller.system_autostart_enabled()
            or self.controller.settings.start_with_windows
        )
        self.action_autostart.blockSignals(False)
        self._apply_window_flags(self.action_on_top.isChecked())

    def _apply_window_flags(self, always_on_top: bool) -> None:
        position = self.pos()
        flags = Qt.FramelessWindowHint | Qt.Window
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.move(position)

    def _toggle_always_on_top(self, checked: bool) -> None:
        self.controller.set_always_on_top(checked)
        self._apply_window_flags(checked)

    def _toggle_autostart(self, checked: bool) -> None:
        ok, message = self.controller.set_start_with_windows(checked)
        if not ok:
            self.action_autostart.blockSignals(True)
            self.action_autostart.setChecked(not checked)
            self.action_autostart.blockSignals(False)
            QMessageBox.warning(self, "开机自启", message)

    def _show_statistics(self) -> None:
        StatisticsDialog(self, self.controller.statistics_service).exec()

    def _show_focus_history(self) -> None:
        from .focus_history_dialog import FocusHistoryDialog

        FocusHistoryDialog(self, self.controller.focus_service).exec()
