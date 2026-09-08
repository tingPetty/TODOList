from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Protocol


BEIJING_TZ = timezone(timedelta(hours=8))


class Clock(Protocol):
    def now(self) -> datetime: ...

    def today(self) -> date: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(BEIJING_TZ)

    def today(self) -> date:
        return self.now().date()
