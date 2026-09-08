from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from ..domain.focus import FocusSession, FocusState
from ..infrastructure.clock import Clock, SystemClock
from ..infrastructure.focus_repository import FocusRepository
from .retention_service import RetentionService


class FocusService:
    def __init__(
        self,
        repository: FocusRepository | None = None,
        clock: Clock | None = None,
        retention: RetentionService | None = None,
    ) -> None:
        self.repository = repository or FocusRepository()
        self.clock = clock or SystemClock()
        self.retention = retention or RetentionService()
        self.state = self.repository.load_state()
        self._sessions = self.repository.load_sessions()
        self.cleanup()

    @property
    def status(self) -> str:
        return self.state.status

    @property
    def current_name(self) -> str:
        return self.state.name

    def sessions(self) -> list[FocusSession]:
        return list(self._sessions)

    def start(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValueError("专注名称不能为空")
        if self.state.status != "idle":
            raise RuntimeError("当前已有专注正在进行")
        timestamp = self._now_iso()
        self.state = FocusState(
            status="running",
            name=name,
            accumulated_seconds=0,
            started_at=timestamp,
            running_since=timestamp,
        )
        self.repository.save_state(self.state)

    def pause(self) -> None:
        self._require_status("running")
        self.state = replace(
            self.state,
            status="paused",
            accumulated_seconds=self.current_elapsed_seconds(),
            running_since=None,
        )
        self.repository.save_state(self.state)

    def resume(self) -> None:
        self._require_status("paused")
        self.state = replace(
            self.state,
            status="running",
            running_since=self._now_iso(),
        )
        self.repository.save_state(self.state)

    def finish(self) -> FocusSession:
        if self.state.status not in {"running", "paused"}:
            raise RuntimeError("当前没有正在进行的专注")
        ended_at = self._now_iso()
        session = FocusSession.create(
            self.state.name,
            self.current_elapsed_seconds(),
            self.state.started_at or ended_at,
            ended_at,
        )
        self._sessions.insert(0, session)
        self._sessions = self.retention.clean_focus_sessions(
            self._sessions, self.clock.today()
        )
        self.repository.save_sessions(self._sessions)
        self.state = FocusState.idle()
        self.repository.save_state(self.state)
        return session

    def delete_session(self, session_id: str) -> None:
        self._sessions = [
            session for session in self._sessions if session.id != session_id
        ]
        self.repository.save_sessions(self._sessions)

    def current_elapsed_seconds(self) -> int:
        elapsed = self.state.accumulated_seconds
        if self.state.status != "running" or not self.state.running_since:
            return max(0, elapsed)
        try:
            running_since = datetime.fromisoformat(self.state.running_since)
            delta = int((self.clock.now() - running_since).total_seconds())
        except (TypeError, ValueError):
            delta = 0
        return max(0, elapsed + delta)

    def cleanup(self) -> None:
        cleaned = self.retention.clean_focus_sessions(
            self._sessions, self.clock.today()
        )
        if len(cleaned) != len(self._sessions):
            self._sessions = cleaned
            self.repository.save_sessions(self._sessions)

    def _now_iso(self) -> str:
        return self.clock.now().isoformat(timespec="seconds")

    def _require_status(self, expected: str) -> None:
        if self.state.status != expected:
            raise RuntimeError(f"当前状态不支持此操作：{self.state.status}")
