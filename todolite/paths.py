from __future__ import annotations

from pathlib import Path
from datetime import datetime


APP_NAME = "DesktopTodoLite"


def app_dir() -> Path:
    # Keep app data inside the project root for easy portability.
    root = Path(__file__).resolve().parents[1]
    path = root / ".data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def tasks_file() -> Path:
    return app_dir() / "tasks.json"


def settings_file() -> Path:
    return app_dir() / "settings.json"


def today_key() -> str:
    return datetime.now().date().isoformat()
