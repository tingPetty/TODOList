from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import os
import tempfile
import uuid

from .paths import tasks_file


@dataclass
class Task:
    id: str
    text: str
    completed: bool
    created_at: str
    order: int

    @staticmethod
    def create(text: str, order: int) -> "Task":
        return Task(
            id=uuid.uuid4().hex,
            text=text,
            completed=False,
            created_at=datetime.now().isoformat(timespec="seconds"),
            order=order,
        )


class TaskStore:
    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or tasks_file()

    def load(self) -> list[Task]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

        items: list[Task] = []
        for i, item in enumerate(raw if isinstance(raw, list) else []):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            items.append(
                Task(
                    id=str(item.get("id") or uuid.uuid4().hex),
                    text=text,
                    completed=bool(item.get("completed", False)),
                    created_at=str(item.get("created_at") or datetime.now().isoformat(timespec="seconds")),
                    order=int(item.get("order", i)),
                )
            )

        items.sort(key=lambda x: x.order)
        return items

    def save(self, tasks: list[Task]) -> None:
        payload = [asdict(t) for t in tasks]
        self._atomic_write_json(self.file_path, payload)

    @staticmethod
    def _atomic_write_json(path: Path, data: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
