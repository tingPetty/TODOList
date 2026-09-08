from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ..presentation.styles.icons import app_icon
from ..presentation.styles.theme import WINDOW_CSS
from ..presentation.windows.main_window import MainWindow
from ..infrastructure.windows_identity import set_app_user_model_id
from .window_controller import WindowController


def run() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    set_app_user_model_id()
    app = QApplication(sys.argv)
    app.setApplicationName("DesktopTodoLite")
    app.setWindowIcon(app_icon())
    app.setStyleSheet(WINDOW_CSS)

    window = MainWindow(WindowController())
    window.show()
    return app.exec()
