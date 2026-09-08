from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from todolite.domain.settings import Settings
from todolite.infrastructure.settings_repository import SettingsRepository
from todolite.infrastructure.task_repository import TaskRepository
from todolite.services.task_service import TaskService


class FakeClock:
    def __init__(self, current_date: date) -> None:
        self.current_date = current_date

    def today(self) -> date:
        return self.current_date


class TodoPageEditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        try:
            from PySide6.QtWidgets import QApplication, QDialog
        except ImportError as error:
            cls._qt_import_error = error
            return

        cls._qt_import_error = None
        cls._qdialog = QDialog
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        if self._qt_import_error is not None:
            self.skipTest(f"PySide6 is unavailable: {self._qt_import_error}")

    def test_clicking_ok_updates_all_edited_fields_and_list_row(self) -> None:
        from todolite.presentation.pages import todo_page as todo_page_module

        service: TaskService
        with TemporaryDirectory() as directory:
            root = Path(directory)
            service = TaskService(
                TaskRepository(root / "tasks.json"),
                SettingsRepository(root / "settings.json"),
                Settings(),
                FakeClock(date(2026, 9, 8)),
            )
            task = service.add_task("原内容", "2026-09-08", False)
            page = todo_page_module.TodoPage(service, lambda: None)

            accepted_code = self._qdialog.Accepted

            class FakeEditDialog:
                def __init__(self, parent, task_to_edit) -> None:
                    self.task_to_edit = task_to_edit

                def exec(self) -> int:
                    return accepted_code

                def values(self) -> tuple[str, str, bool]:
                    return "新内容", "2026-09-09", True

            original_dialog = todo_page_module.TaskEditDialog
            todo_page_module.TaskEditDialog = FakeEditDialog
            try:
                page._edit_task(task.id)
            finally:
                todo_page_module.TaskEditDialog = original_dialog

            updated = next(item for item in service.tasks if item.id == task.id)
            self.assertEqual(updated.text, "新内容")
            self.assertEqual(updated.task_date, "2026-09-09")
            self.assertTrue(updated.important)

            self.assertEqual(page.task_list.count(), 2)
            item = page.task_list.item(1)
            row = page.task_list.itemWidget(item)
            self.assertEqual(item.data(todo_page_module.TASK_DATE_ROLE), "2026-09-09")
            self.assertEqual(row.text_label.text(), "❗ 新内容")
            self.assertTrue(row.important)

            page.close()
            page.deleteLater()
            self._app.processEvents()


if __name__ == "__main__":
    unittest.main()
