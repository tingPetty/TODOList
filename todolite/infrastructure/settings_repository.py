from __future__ import annotations

from ..domain.settings import Settings
from .json_store import JsonStore
from .paths import settings_file


class SettingsRepository:
    def __init__(self, file_path=None) -> None:
        self.file_path = file_path or settings_file()

    def load(self) -> Settings:
        return Settings.from_dict(JsonStore.load(self.file_path, {}))

    def save(self, settings: Settings) -> None:
        JsonStore.save(self.file_path, settings.to_dict())
