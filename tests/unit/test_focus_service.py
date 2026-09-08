from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from todolite.infrastructure.focus_repository import FocusRepository
from todolite.services.focus_service import FocusService


BEIJING = timezone(timedelta(hours=8))


class FakeClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 8, 29, 10, 0, tzinfo=BEIJING)

    def now(self) -> datetime:
        return self.current

    def today(self) -> date:
        return self.current.date()

    def advance(self, seconds: int) -> None:
        self.current += timedelta(seconds=seconds)


class FocusServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.clock = FakeClock()
        self.repository = FocusRepository(root / "sessions.json", root / "state.json")
        self.service = FocusService(self.repository, self.clock)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_start_pause_resume_finish(self) -> None:
        self.service.start("deep work")
        self.clock.advance(12)
        self.assertEqual(self.service.current_elapsed_seconds(), 12)
        self.service.pause()
        self.clock.advance(100)
        self.assertEqual(self.service.current_elapsed_seconds(), 12)
        self.service.resume()
        self.clock.advance(8)
        session = self.service.finish()

        self.assertEqual(session.name, "deep work")
        self.assertEqual(session.duration_seconds, 20)
        self.assertEqual(self.service.status, "idle")

    def test_running_state_survives_service_recreation(self) -> None:
        self.service.start("restore me")
        self.clock.advance(5)
        restored = FocusService(self.repository, self.clock)
        self.assertEqual(restored.status, "running")
        self.assertEqual(restored.current_name, "restore me")
        self.assertEqual(restored.current_elapsed_seconds(), 5)

    def test_delete_session(self) -> None:
        self.service.start("remove me")
        session = self.service.finish()
        self.service.delete_session(session.id)
        self.assertEqual(self.service.sessions(), [])


if __name__ == "__main__":
    unittest.main()
