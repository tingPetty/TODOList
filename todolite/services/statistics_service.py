from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from ..infrastructure.clock import Clock, SystemClock
from ..infrastructure.task_repository import TaskRepository


class StatisticsService:
    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        clock: Clock | None = None,
        task_service=None,
    ) -> None:
        self.task_repository = task_repository
        self.task_service = task_service
        self.clock = clock or SystemClock()

    def _tasks(self):
        if self.task_service is not None:
            return self.task_service.all_tasks()
        if self.task_repository is not None:
            return self.task_repository.load()
        return []

    def completion_curve(self, days: int = 30) -> tuple[list[str], list[int]]:
        days = max(1, int(days))
        start = self.clock.today() - timedelta(days=days - 1)
        date_keys = [(start + timedelta(days=i)).isoformat() for i in range(days)]
        counts: dict[str, int] = defaultdict(int)
        for task in self._tasks():
            if task.completed:
                counts[task.task_date] += 1
        return date_keys, [counts.get(key, 0) for key in date_keys]

    def completed_on(self, date_key: str):
        return sorted(
            [task for task in self._tasks() if task.completed and task.task_date == date_key],
            key=lambda task: (task.order, task.created_at, task.id),
        )
