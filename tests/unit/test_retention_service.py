from __future__ import annotations

from datetime import date
import unittest

from todolite.domain.focus import FocusSession
from todolite.services.retention_service import RetentionService


class RetentionServiceTests(unittest.TestCase):
    def test_focus_records_keep_seven_calendar_days(self) -> None:
        service = RetentionService()
        old = FocusSession.create(
            "old", 1, "2026-08-22T10:00:00+08:00", "2026-08-22T10:00:01+08:00"
        )
        boundary = FocusSession.create(
            "boundary", 1, "2026-08-23T10:00:00+08:00", "2026-08-23T10:00:01+08:00"
        )
        kept = service.clean_focus_sessions([old, boundary], date(2026, 8, 29))
        self.assertEqual([session.name for session in kept], ["boundary"])


if __name__ == "__main__":
    unittest.main()
