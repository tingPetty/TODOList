from __future__ import annotations

from ..domain.task import Task
from .json_store import JsonStore
from .paths import tasks_file


class TaskRepository:
    def __init__(self, file_path=None) -> None:
        self.file_path = file_path or tasks_file()

    def load(self) -> list[Task]:
        raw = JsonStore.load(self.file_path, [])
        if not isinstance(raw, list):
            return []
        tasks: list[Task] = []
        for index, item in enumerate(raw):
            task = Task.from_dict(item, index)
            if task is not None:
                tasks.append(task)
        tasks.sort(key=lambda task: task.order)
        return tasks

    def save(self, tasks: list[Task]) -> None:
        JsonStore.save(self.file_path, [task.to_dict() for task in tasks])
