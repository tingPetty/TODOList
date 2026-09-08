from __future__ import annotations

import sys
from pathlib import Path


APP_NAME = "DesktopTodoLite"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else PROJECT_ROOT
)


def app_dir() -> Path:
    path = DATA_ROOT / ".data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def tasks_file() -> Path:
    return app_dir() / "tasks.json"


def settings_file() -> Path:
    return app_dir() / "settings.json"


def focus_sessions_file() -> Path:
    return app_dir() / "focus_sessions.json"


def focus_state_file() -> Path:
    return app_dir() / "focus_state.json"


def resource_path(relative_path: str) -> Path:
    """Resolve a bundled resource both from source and PyInstaller builds."""
    bundle_root = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return bundle_root / relative_path
