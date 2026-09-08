from __future__ import annotations

from ..domain.focus import FocusSession, FocusState
from .json_store import JsonStore
from .paths import focus_sessions_file, focus_state_file


class FocusRepository:
    def __init__(self, sessions_path=None, state_path=None) -> None:
        self.sessions_path = sessions_path or focus_sessions_file()
        self.state_path = state_path or focus_state_file()

    def load_sessions(self) -> list[FocusSession]:
        raw = JsonStore.load(self.sessions_path, [])
        if not isinstance(raw, list):
            return []
        sessions = [
            session
            for item in raw
            if (session := FocusSession.from_dict(item)) is not None
        ]
        return sorted(sessions, key=lambda session: session.ended_at, reverse=True)

    def save_sessions(self, sessions: list[FocusSession]) -> None:
        JsonStore.save(
            self.sessions_path,
            [session.to_dict() for session in sessions],
        )

    def load_state(self) -> FocusState:
        return FocusState.from_dict(JsonStore.load(self.state_path, {}))

    def save_state(self, state: FocusState) -> None:
        JsonStore.save(self.state_path, state.to_dict())
