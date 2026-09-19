"""UI regressions use temporary repositories, never the user's .data directory."""
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox

from todolite.domain.settings import Settings
from todolite.infrastructure.focus_repository import FocusRepository
from todolite.infrastructure.settings_repository import SettingsRepository
from todolite.infrastructure.task_repository import TaskRepository
from todolite.services.focus_service import FocusService
from todolite.services.task_service import TaskService
from todolite.services.statistics_service import StatisticsService
from todolite.presentation.styles.theme import apply_theme
from todolite.presentation.windows.main_window import MainWindow
from todolite.presentation.windows.focus_history_dialog import FocusHistoryDialog
from todolite.presentation.dialogs.statistics_dialog import StatisticsDialog
from todolite.presentation.dialogs.task_edit_dialog import TaskEditDialog
from todolite.presentation.widgets.empty_state import EmptyState


class Clock:
    current = datetime(2026, 9, 19, 10, tzinfo=timezone(timedelta(hours=8)))

    def now(self):
        return self.current

    def today(self):
        return self.current.date()


class PreviewController:
    def __init__(self, root):
        self.clock = Clock()
        self.settings = Settings()
        self.task_service = TaskService(TaskRepository(root / "tasks.json"),
                                        SettingsRepository(root / "settings.json"),
                                        self.settings, self.clock)
        self.focus_service = FocusService(FocusRepository(root / "sessions.json", root / "state.json"), self.clock)
        self.statistics_service = StatisticsService(clock=self.clock, task_service=self.task_service)

    def system_autostart_enabled(self):
        return False

    def set_always_on_top(self, enabled):
        self.settings.always_on_top = enabled

    def set_start_with_windows(self, enabled):
        self.settings.start_with_windows = enabled
        return True, ""


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        # Windows' offscreen platform has no system font discovery.
        if not QFontDatabase.families():
            for font in ("msyh.ttc", "consola.ttf"):
                path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / font
                if path.exists():
                    QFontDatabase.addApplicationFont(str(path))
        apply_theme(cls.app)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.controller = PreviewController(Path(self.temp.name))
        self.window = MainWindow(self.controller)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.focus_page.timer.stop()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def capture(self, widget, name):
        self.app.processEvents()
        directory = os.environ.get("TODO_SCREENSHOTS")
        if directory:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            self.assertTrue(widget.grab().save(str(path / f"{name}.png")))

    def test_empty_refresh_add_and_checkbox_only_completion(self):
        page = self.window.todo_page
        self.capture(self.window, "todo-empty")
        for _ in range(3):
            page.refresh()
        self.assertEqual(len(page.findChildren(EmptyState)), 1)
        page.input_box.setText("跑实验")
        QTest.mouseClick(page.add_button, Qt.LeftButton)
        self.assertEqual(len(self.controller.task_service.tasks), 1)
        row = page.task_list.itemWidget(page.task_list.item(1))
        QTest.mouseClick(row.text_label, Qt.LeftButton)
        self.assertFalse(self.controller.task_service.tasks[0].completed)
        checkbox = row.findChild(QCheckBox)
        QTest.mouseClick(checkbox, Qt.LeftButton)
        self.assertTrue(self.controller.task_service.tasks[0].completed)
        self.assertFalse(page._empty_state.isVisible())

    def test_calendar_menu_and_empty_history(self):
        calendar = self.window.todo_page.date_picker.calendarWidget()
        calendar.resize(320, 260)
        calendar.show()
        self.capture(calendar, "calendar")
        calendar.hide()
        menu = self.window.menu_button.menu()
        menu.show()
        self.capture(menu, "menu")
        menu.hide()
        history = FocusHistoryDialog(self.window, self.controller.focus_service)
        history.show()
        self.capture(history, "history-empty")
        history.close()

    def test_resources_and_long_running_timer(self):
        from todolite.presentation.styles.icons import ui_icon, app_icon
        from todolite.presentation.widgets.sprout import Sprout
        for name in ("check", "clock", "trash", "play", "history", "chart", "star", "plus", "pause", "stop", "more", "close"):
            self.assertFalse(ui_icon(name).pixmap(24, 24).isNull(), name)
        self.assertFalse(app_icon().pixmap(32, 32).isNull())
        for state in ("idle", "running", "paused", "happy"):
            sprout = Sprout()
            sprout.set_state(state)
            self.assertTrue(sprout.renderer().isValid())
        self.window._switch_page(1)
        self.window.resize(360, 360)
        page = self.window.focus_page
        page.name_input.setText("一个很长的专注名称" * 30)
        page._start()
        self.controller.clock.current += timedelta(hours=123, seconds=45)
        page.refresh()
        self.app.processEvents()
        self.assertEqual(page.timer_label.text(), "123:00:45")
        self.assertLessEqual(page.timer_label.fontMetrics().horizontalAdvance(page.timer_label.text()), page.timer_label.width())
        self.capture(self.window, "focus-long")

    def test_focus_validation_survives_timer_and_page_switch(self):
        self.window._switch_page(1)
        page = self.window.focus_page
        page._start()
        page.refresh()
        self.assertEqual(page.status_label.text(), "请先填写专注名称")
        page.name_input.setText("整理旅游购票时间")
        page._start()
        self.controller.clock.current += timedelta(seconds=1122)
        self.window._switch_page(0)
        page.refresh()
        self.window._switch_page(1)
        self.assertEqual(page.timer_label.text(), "00:18:42")
        self.capture(self.window, "focus-running")
        page._pause_or_resume()
        self.controller.clock.current += timedelta(seconds=90)
        page.refresh()
        self.assertEqual(page.timer_label.text(), "00:18:42")
        self.capture(self.window, "focus-paused")
        page._finish()
        self.assertEqual(self.controller.focus_service.sessions()[0].duration_seconds, 1122)
        self.assertIn("已保存", page.status_label.text())
        self.capture(self.window, "focus-saved")

    def test_growth_boundaries_pause_restore_and_new_session(self):
        self.assertEqual(self.window.windowTitle(), "小芽日记")
        self.window._switch_page(1)
        page = self.window.focus_page
        page.name_input.setText("让专注慢慢开花")
        page._start()
        clock = self.controller.clock
        clock.current += timedelta(seconds=1199)
        page.refresh()
        self.assertEqual(page.sprout.stage, "sprout")
        clock.current += timedelta(seconds=1)
        page.refresh()
        self.assertEqual(page.sprout.stage, "bud")
        self.capture(self.window, "focus-bud")
        page._pause_or_resume()
        clock.current += timedelta(hours=2)
        page.refresh()
        self.assertEqual(page.sprout.stage, "bud")
        self.assertEqual(page.sprout._state, "paused")
        self.assertEqual(page.timer_label.text(), "00:20:00")
        self.capture(self.window, "focus-bud-paused")
        page._pause_or_resume()
        clock.current += timedelta(seconds=1199)
        page.refresh()
        self.assertEqual(page.sprout.stage, "bud")
        clock.current += timedelta(seconds=1)
        page.refresh()
        self.assertEqual(page.sprout.stage, "flower")
        self.capture(self.window, "focus-flower")
        page._pause_or_resume()
        page.focus_service = FocusService(page.focus_service.repository, clock)
        page.refresh()
        self.assertEqual(page.sprout.stage, "flower")
        self.assertEqual(page.sprout._state, "paused")
        self.capture(self.window, "focus-flower-paused")
        page._finish()
        self.assertEqual(page.sprout.stage, "flower")
        self.assertEqual(page.sprout._state, "happy")
        page._clear_feedback()
        self.assertEqual(page.sprout.stage, "sprout")
        page.name_input.setText("新的一段专注")
        page._start()
        self.assertEqual(page.sprout.stage, "sprout")

    def test_all_growth_expressions_load(self):
        from todolite.presentation.widgets.sprout import Sprout
        sprout = Sprout()
        for seconds in (0, 1200, 2400):
            for state in ("running", "paused", "happy"):
                sprout.set_state(state, seconds)
                self.assertTrue(sprout.renderer().isValid(), (seconds, state))

    def test_default_and_minimum_layout_with_long_text(self):
        service = self.controller.task_service
        for text, important in [("跑实验", False), ("投两家公司", True), ("整理百度面经", False), ("改一下简历排版", False)]:
            task = service.add_task(text, "2026-09-19", important)
        service.toggle_task(task.id, True)
        self.window.todo_page.refresh()
        self.capture(self.window, "todo")
        service.add_task("一段非常长的任务名称" * 20, "2026-09-19", False)
        self.window.todo_page.refresh()
        self.window.resize(360, 360)
        self.app.processEvents()
        self.assertEqual((self.window.width(), self.window.height()), (360, 360))
        page = self.window.todo_page
        self.assertGreaterEqual(page.input_box.width(), 160)
        self.assertGreaterEqual(page.task_list.height(), 80)
        self.capture(self.window, "todo-compact")
        self.window._switch_page(1)
        self.app.processEvents()
        self.assertEqual(self.window.height(), 360)
        self.assertTrue(self.window.rect().contains(self.window.focus_page.start_button.mapTo(self.window, self.window.focus_page.start_button.rect().bottomRight())))
        self.capture(self.window, "focus-compact")
        self.window.resize(430, 420)
        self.capture(self.window, "focus-idle")

    def test_dialogs_empty_data_long_names_and_chart_query(self):
        stats = StatisticsDialog(self.window, self.controller.statistics_service)
        stats.show()
        self.capture(stats, "statistics-empty")
        self.assertTrue(stats.empty_state.isVisible())
        stats.close()
        service = self.controller.task_service
        for day, count in [("2026-09-01", 2), ("2026-09-04", 4), ("2026-09-09", 1), ("2026-09-13", 3), ("2026-09-19", 2)]:
            for index in range(count):
                task = service.add_task(f"整理资料 {index + 1}", day, False)
                service.toggle_task(task.id, True)
        stats = StatisticsDialog(self.window, self.controller.statistics_service)
        stats.show()
        self.capture(stats, "statistics")
        self.assertEqual(stats.detail_list.count(), 2)
        stats.close()
        focus = self.controller.focus_service
        for name, seconds in [("整理旅游购票时间", 6857), ("学习", 6097), ("研究各个景点预约时间和路线" * 4, 1915)]:
            focus.start(name)
            self.controller.clock.current += timedelta(seconds=seconds)
            focus.finish()
        history = FocusHistoryDialog(self.window, focus)
        history.show()
        self.capture(history, "history")
        self.assertEqual(history.width(), 390)
        history.close()
        edit = TaskEditDialog(self.window, task)
        edit.show()
        self.capture(edit, "edit")
        edit.text_input.clear()
        edit.accept()
        self.assertTrue(edit.error_label.isVisible())
        edit.close()


if __name__ == "__main__":
    unittest.main()
