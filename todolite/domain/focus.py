from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal
import uuid


FocusStatus = Literal["idle", "running", "paused"]


@dataclass(frozen=True)
class FocusSession:
    id: str
    name: str
    duration_seconds: int
    started_at: str
    ended_at: str

    @staticmethod
    def create(
        name: str,
        duration_seconds: int,
        started_at: str,
        ended_at: str,
    ) -> "FocusSession":
        return FocusSession(
            id=uuid.uuid4().hex,
            name=name.strip(),
            duration_seconds=max(0, int(duration_seconds)),
            started_at=started_at,
            ended_at=ended_at,
        )

    @classmethod
    def from_dict(cls, item: object) -> "FocusSession | None":
        if not isinstance(item, dict):
            return None
        name = str(item.get("name", "")).strip()
        started_at = str(item.get("started_at", ""))
        ended_at = str(item.get("ended_at", ""))
        if not name or not started_at or not ended_at:
            return None
        try:
            duration = max(0, int(item.get("duration_seconds", 0)))
        except (TypeError, ValueError):
            duration = 0
        return cls(
            id=str(item.get("id") or uuid.uuid4().hex),
            name=name,
            duration_seconds=duration,
            started_at=started_at,
            ended_at=ended_at,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FocusState:
    status: FocusStatus = "idle"
    name: str = ""
    accumulated_seconds: int = 0
    started_at: str | None = None
    running_since: str | None = None

    @classmethod
    def idle(cls) -> "FocusState":
        return cls()

    @classmethod
    def from_dict(cls, item: object) -> "FocusState":
        if not isinstance(item, dict):
            return cls.idle()
        status = item.get("status", "idle")
        if status not in {"idle", "running", "paused"}:
            status = "idle"
        try:
            accumulated = max(0, int(item.get("accumulated_seconds", 0)))
        except (TypeError, ValueError):
            accumulated = 0
        name = str(item.get("name", "")).strip()
        started_at = item.get("started_at")
        running_since = item.get("running_since")
        if status == "idle" or not name or not started_at:
            return cls.idle()
        return cls(
            status=status,
            name=name,
            accumulated_seconds=accumulated,
            started_at=str(started_at),
            running_since=str(running_since) if running_since else None,
        )

    def to_dict(self) -> dict:
        return asdict(self)
