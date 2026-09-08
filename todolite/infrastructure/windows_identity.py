from __future__ import annotations

import sys


APP_USER_MODEL_ID = "DesktopTodoLite.App"


def set_app_user_model_id() -> None:
    """Give Windows a stable identity for taskbar grouping and icon lookup."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_USER_MODEL_ID
        )
    except (AttributeError, OSError):  # pragma: no cover - Windows shell only
        pass
