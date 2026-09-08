from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import date, timedelta

from ..domain.settings import Settings
from ..domain.task import Task, TaskDisplayGroup
from ..infrastructure.clock import Clock, SystemClock
from ..infrastructure.settings_repository import SettingsRepository
from ..infrastructure.task_repository import TaskRepository
from .retention_service import RetentionService


class TaskService:
    DISPLAY_HIDE_COMPLETED_DAYS = 2

    def __init__(
        self,
        repository: TaskRepository | None = None,
        settings_repository: SettingsRepository | None = None,
        settings: Settings | None = None,
        clock: Clock | None = None,
        retention: RetentionService | None = None,
    ) -> None:
        self.repository = repository or TaskRepository()
        self.settings_repository = settings_repository or SettingsRepository()
        self.clock = clock or SystemClock()
        self.retention = retention or RetentionService()
        self.settings = settings or self.settings_repository.load()
        self._tasks = self.repository.load()
        self._cleanup_expired_completed_records()

    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks)

    def all_tasks(self) -> list[Task]:
        return self.tasks

    def add_task(self, text: str, task_date: str, important: bool = False) -> Task:
        text = text.strip()
        if not text:
            raise ValueError("任务内容不能为空")
        task = Task.create(
            text,
            order=self._next_order_for_date(task_date),
            task_date=task_date,
            important=important,
        )
        self._tasks.append(task)
        self._persist()
        return task

    def toggle_task(self, task_id: str, completed: bool) -> None:
        for index, task in enumerate(self._tasks):
            if task.id != task_id:
                continue
            if completed:
                self._tasks[index] = replace(task, completed=True)
            else:
                self._tasks[index] = replace(
                    task,
                    completed=False,
                    order=self._next_order_for_date(task.task_date),
                )
            break
        self._reindex_active_order()
        self._persist()

    def delete_task(self, task_id: str) -> None:
        self._tasks = [task for task in self._tasks if task.id != task_id]
        self._reindex_active_order()
        self._persist()

    def edit_task(
        self,
        task_id: str,
        text: str,
        task_date: str,
        important: bool,
    ) -> None:
        text = text.strip()
        if not text:
            raise ValueError("任务内容不能为空")
        for index, task in enumerate(self._tasks):
            if task.id != task_id:
                continue
            next_order = task.order
            if not task.completed and task.task_date != task_date:
                next_order = self._next_order_for_date(task_date)
            self._tasks[index] = replace(
                task,
                text=text,
                task_date=task_date,
                important=important,
                order=next_order,
            )
            break
        self._reindex_active_order()
        self._persist()

    def reorder_tasks(self, ordered_items: list[tuple[str, str]]) -> None:
        counters: dict[str, int] = defaultdict(int)
        updates: dict[str, tuple[int, str]] = {}
        for task_id, date_key in ordered_items:
            date_key = str(date_key)
            updates[str(task_id)] = (counters[date_key], date_key)
            counters[date_key] += 1

        changed = False
        for index, task in enumerate(self._tasks):
            if task.id not in updates or task.completed:
                continue
            next_order, next_date = updates[task.id]
            if task.order != next_order or task.task_date != next_date:
                self._tasks[index] = replace(
                    task, order=next_order, task_date=next_date
                )
                changed = True
        if changed:
            self._persist(cleanup=False)

    def display_groups(self) -> list[TaskDisplayGroup]:
        grouped: dict[str, list[Task]] = defaultdict(list)
        for task in self._tasks:
            grouped[task.task_date].append(task)

        hide_before_or_on = self._display_hide_before_or_on()
        result: list[TaskDisplayGroup] = []
        for date_key in sorted(grouped, reverse=True):
            tasks = sorted(
                grouped[date_key],
                key=lambda task: (
                    task.completed,
                    not task.important,
                    task.order,
                    task.created_at,
                    task.id,
                ),
            )
            active = tuple(task for task in tasks if not task.completed)
            completed = tuple(
                task
                for task in tasks
                if task.completed and task.task_date > hide_before_or_on
            )
            if active or completed:
                result.append(TaskDisplayGroup(date_key, active, completed))
        return result

    def is_group_collapsed(self, date_key: str) -> bool:
        return bool(self.settings.collapsed_completed_dates.get(date_key, False))

    def toggle_completed_group(self, date_key: str) -> None:
        if self.is_group_collapsed(date_key):
            self.settings.collapsed_completed_dates.pop(date_key, None)
        else:
            self.settings.collapsed_completed_dates[date_key] = True
        self.settings_repository.save(self.settings)

    def date_label(self, date_key: str) -> str:
        return "今天" if date_key == self.clock.today().isoformat() else date_key

    def cleanup(self) -> None:
        self._cleanup_expired_completed_records()

    def _display_hide_before_or_on(self) -> str:
        return (
            self.clock.today() - timedelta(days=self.DISPLAY_HIDE_COMPLETED_DAYS)
        ).isoformat()

    def _next_order_for_date(self, date_key: str) -> int:
        active = [
            task.order
            for task in self._tasks
            if task.task_date == date_key and not task.completed
        ]
        return max(active) + 1 if active else 0

    def _reindex_active_order(self) -> None:
        counters: dict[str, int] = defaultdict(int)
        updated: list[Task] = []
        for task in sorted(
            self._tasks,
            key=lambda item: (
                item.task_date,
                item.completed,
                not item.important,
                item.order,
                item.created_at,
                item.id,
            ),
        ):
            if task.completed:
                updated.append(task)
                continue
            updated.append(replace(task, order=counters[task.task_date]))
            counters[task.task_date] += 1
        self._tasks = updated

    def _cleanup_expired_completed_records(self) -> None:
        kept = self.retention.clean_tasks(self._tasks, self.clock.today())
        if len(kept) != len(self._tasks):
            self._tasks = kept
            self._reindex_active_order()
            self.repository.save(self._tasks)

    def _persist(self, *, cleanup: bool = True) -> None:
        if cleanup:
            self._cleanup_expired_completed_records()
        self.repository.save(self._tasks)
