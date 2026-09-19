from __future__ import annotations

from PySide6.QtGui import QIcon

from ...infrastructure.paths import resource_path


def ui_icon(name: str, *, light: bool = False) -> QIcon:
    suffix = "-white" if light else ""
    return QIcon(str(resource_path(f"assets/ui/{name}{suffix}.svg")))


def app_icon() -> QIcon:
    svg_path = resource_path("assets/icon.svg")
    ico_path = resource_path("assets/icon.ico")
    return QIcon(str(svg_path if svg_path.exists() else ico_path))
