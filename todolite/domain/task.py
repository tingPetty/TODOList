from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class Task:
    id: str
    text: str
    completed: bool
    created_at: str
    task_date: str
    important: bool
    order: int

    @staticmethod
    def create(text: str, order: int, task_date: str, important: bool = False) -> "Task":
        return Task(
            id=uuid.uuid4().hex,
            text=text.strip(),
            completed=False,
            created_at=datetime.now().isoformat(timespec="seconds"),
            task_date=task_date,
            important=important,
            order=order,
        )

    @classmethod
    def from_dict(cls, item: object, fallback_order: int) -> "Task | None":
        if not isinstance(item, dict):
            return None
        text = str(item.get("text", "")).strip()
        if not text:
            return None
        created_at = str(
            item.get("created_at") or datetime.now().isoformat(timespec="seconds")
        )
        task_date = str(item.get("task_date") or created_at[:10])
        try:
            order = int(item.get("order", fallback_order))
        except (TypeError, ValueError):
            order = fallback_order
        return cls(
            id=str(item.get("id") or uuid.uuid4().hex),
            text=text,
            completed=bool(item.get("completed", False)),
            created_at=created_at,
            task_date=task_date,
            important=bool(item.get("important", False)),
            order=order,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class TaskDisplayGroup:
    date_key: str
    active_tasks: tuple[Task, ...]
    completed_tasks: tuple[Task, ...]
