from __future__ import annotations

from ..domain.settings import Settings
from ..infrastructure import autostart
from ..infrastructure.clock import SystemClock
from ..infrastructure.focus_repository import FocusRepository
from ..infrastructure.settings_repository import SettingsRepository
from ..infrastructure.task_repository import TaskRepository
from ..services.focus_service import FocusService
from ..services.retention_service import RetentionService
from ..services.statistics_service import StatisticsService
from ..services.task_service import TaskService


class WindowController:
    """Composes application services and handles cross-page app settings."""

    def __init__(self) -> None:
        self.clock = SystemClock()
        self.retention = RetentionService()
        self.settings_repository = SettingsRepository()
        self.settings: Settings = self.settings_repository.load()
        self.autostart_sync_error: str | None = None
        if self.settings.start_with_windows or autostart.is_enabled():
            ok, message = autostart.ensure_current_command()
            if not ok:
                self.autostart_sync_error = message
        self.task_service = TaskService(
            TaskRepository(),
            self.settings_repository,
            self.settings,
            self.clock,
            self.retention,
        )
        self.focus_service = FocusService(
            FocusRepository(), self.clock, self.retention
        )
        self.statistics_service = StatisticsService(
            clock=self.clock, task_service=self.task_service
        )

    def set_always_on_top(self, enabled: bool) -> None:
        self.settings.always_on_top = bool(enabled)
        self.settings_repository.save(self.settings)

    def set_start_with_windows(self, enabled: bool) -> tuple[bool, str]:
        ok, message = autostart.set_enabled(enabled)
        if ok:
            self.settings.start_with_windows = bool(enabled)
            self.settings_repository.save(self.settings)
        return ok, message

    def system_autostart_enabled(self) -> bool:
        return autostart.is_enabled()
