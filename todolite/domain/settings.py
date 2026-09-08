from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Settings:
    always_on_top: bool = False
    start_with_windows: bool = False
    collapsed_completed_dates: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: object) -> "Settings":
        if not isinstance(data, dict):
            return cls()
        collapsed = data.get("collapsed_completed_dates", {})
        collapsed_map = (
            {str(key): bool(value) for key, value in collapsed.items()}
            if isinstance(collapsed, dict)
            else {}
        )
        return cls(
            always_on_top=bool(data.get("always_on_top", False)),
            start_with_windows=bool(data.get("start_with_windows", False)),
            collapsed_completed_dates=collapsed_map,
        )

    def to_dict(self) -> dict:
        return {
            "always_on_top": self.always_on_top,
            "start_with_windows": self.start_with_windows,
            "collapsed_completed_dates": dict(self.collapsed_completed_dates),
        }
