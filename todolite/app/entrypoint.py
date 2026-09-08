"""PyInstaller entrypoint for the DesktopTodoLite executable."""

from __future__ import annotations

from todolite.app import run


if __name__ == "__main__":
    raise SystemExit(run())
