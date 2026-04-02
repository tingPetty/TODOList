from __future__ import annotations

import sys
from pathlib import Path

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "DesktopTodoLite"


def _build_command() -> str:
    exe = Path(sys.executable)
    if getattr(sys, "frozen", False):
        return f'"{exe}"'

    script = Path(sys.argv[0]).resolve()
    return f'"{exe}" "{script}"'


def is_enabled() -> bool:
    if winreg is None:
        return False

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, RUN_VALUE_NAME)
            return bool(value)
    except OSError:
        return False


def set_enabled(enabled: bool) -> tuple[bool, str]:
    if winreg is None:
        return False, "当前平台不支持开机自启。"

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, RUN_VALUE_NAME, 0, winreg.REG_SZ, _build_command())
            else:
                try:
                    winreg.DeleteValue(key, RUN_VALUE_NAME)
                except FileNotFoundError:
                    pass
    except OSError as e:
        return False, f"操作启动项失败: {e}"

    return True, ""
