"""Small vector companion; no looping animation or business state of its own."""
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from ...infrastructure.paths import resource_path


class Sprout(QSvgWidget):
    def __init__(self, size: int = 64, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._state = ""
        self.stage = ""
        self.set_state("idle")

    def set_state(self, state: str, elapsed_seconds: int = 0) -> None:
        state = state if state in {"idle", "running", "paused", "happy"} else "idle"
        stage = ("flower" if elapsed_seconds >= 40 * 60 else
                 "bud" if elapsed_seconds >= 20 * 60 else "sprout")
        if state == "idle":
            stage = "sprout"
        if (state, stage) != (self._state, self.stage):
            self._state = state
            self.stage = stage
            filename = state if stage == "sprout" else f"{stage}-{state}"
            self.load(str(resource_path(f"assets/sprout/{filename}.svg")))
            name = {"sprout": "小芽", "bud": "花苞", "flower": "开花"}[stage]
            self.setAccessibleName(f"{name} · {'休息中' if state == 'paused' else '专注成长'}")
