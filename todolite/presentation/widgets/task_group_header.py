from __future__ import annotations

from collections.abc import Callable

from .section_header import SectionHeader


class TaskGroupHeader(SectionHeader):
    def __init__(
        self,
        text: str,
        completed_count: int,
        collapsed: bool,
        on_toggle: Callable[[], None],
        parent=None,
    ) -> None:
        action_text = None
        if completed_count:
            action_text = (
                f"展开已完成 {completed_count}"
                if collapsed
                else f"收起已完成 {completed_count}"
            )
        super().__init__(
            text,
            action_text=action_text,
            action_tooltip="展开或收起已完成任务" if completed_count else None,
            on_action=on_toggle if completed_count else None,
            parent=parent,
        )
