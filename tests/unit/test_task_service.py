from __future__ import annotations

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


class TaskServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.service = TaskService(
            TaskRepository(root / "tasks.json"),
            SettingsRepository(root / "settings.json"),
            Settings(),
            FakeClock(date(2026, 8, 29)),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_task_lifecycle_and_cross_date_reorder(self) -> None:
        first = self.service.add_task(" first ", "2026-08-29", True)
        second = self.service.add_task("second", "2026-08-30")
        self.service.edit_task(second.id, "updated", "2026-08-29", False)
        self.service.reorder_tasks([(second.id, "2026-08-29"), (first.id, "2026-08-29")])

        updated = next(task for task in self.service.tasks if task.id == second.id)
        self.assertEqual(updated.text, "updated")
        self.assertEqual(updated.task_date, "2026-08-29")
        self.service.toggle_task(first.id, True)
        self.assertTrue(next(task for task in self.service.tasks if task.id == first.id).completed)
        self.service.delete_task(second.id)
        self.assertEqual(len(self.service.tasks), 1)

    def test_old_completed_task_is_hidden_but_recent_task_is_displayed(self) -> None:
        old = self.service.add_task("old", "2026-08-26")
        recent = self.service.add_task("recent", "2026-08-29")
        self.service.toggle_task(old.id, True)
        self.service.toggle_task(recent.id, True)

        groups = self.service.display_groups()
        self.assertEqual([group.date_key for group in groups], ["2026-08-29"])

    def test_completed_task_older_than_thirty_days_is_cleaned(self) -> None:
        expired = self.service.add_task("expired", "2026-07-30")
        self.service.toggle_task(expired.id, True)
        self.assertEqual(self.service.tasks, [])


if __name__ == "__main__":
    unittest.main()
