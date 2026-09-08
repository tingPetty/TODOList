from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

from ..domain.task import Task


class RetentionService:
    TASK_RETENTION_DAYS = 30
    FOCUS_RETENTION_DAYS = 7

    def clean_tasks(self, tasks: Iterable[Task], today: date) -> list[Task]:
        keep_from = today - timedelta(days=self.TASK_RETENTION_DAYS - 1)
        return [
            task
            for task in tasks
            if not (task.completed and task.task_date < keep_from.isoformat())
        ]

    def clean_focus_sessions(self, sessions, today: date):
        keep_from = today - timedelta(days=self.FOCUS_RETENTION_DAYS - 1)
        return [
            session
            for session in sessions
            if session.ended_at[:10] >= keep_from.isoformat()
        ]
