from __future__ import annotations

from pathlib import Path
import json
import os
import tempfile

from .paths import settings_file


DEFAULT_SETTINGS = {
    "always_on_top": False,
    "start_with_windows": False,
    "collapsed_completed_dates": {},
}


class SettingsStore:
    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or settings_file()

    def load(self) -> dict:
        if not self.file_path.exists():
            return DEFAULT_SETTINGS.copy()

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return DEFAULT_SETTINGS.copy()

        result = DEFAULT_SETTINGS.copy()
        if isinstance(data, dict):
            collapsed = data.get("collapsed_completed_dates", {})
            collapsed_map = {
                str(k): bool(v) for k, v in collapsed.items()
            } if isinstance(collapsed, dict) else {}
            result.update(
                {
                    "always_on_top": bool(data.get("always_on_top", False)),
                    "start_with_windows": bool(data.get("start_with_windows", False)),
                    "collapsed_completed_dates": collapsed_map,
                }
            )
        return result

    def save(self, settings: dict) -> None:
        data = {
            "always_on_top": bool(settings.get("always_on_top", False)),
            "start_with_windows": bool(settings.get("start_with_windows", False)),
            "collapsed_completed_dates": {
                str(k): bool(v)
                for k, v in settings.get("collapsed_completed_dates", {}).items()
            },
        }
        self._atomic_write_json(self.file_path, data)

    @staticmethod
    def _atomic_write_json(path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
