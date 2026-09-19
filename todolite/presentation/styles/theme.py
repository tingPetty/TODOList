"""Little Sprout: opaque paper surfaces and shared green controls."""
from ...infrastructure.paths import resource_path

COLORS = {
    "canvas": "#F6F8ED", "paper": "#FFFEF7", "soft": "#E8F0D9",
    "primary": "#3F6B45", "hover": "#345A3A", "pressed": "#294A30",
    "accent": "#BBD78C", "ink": "#263C2D", "muted": "#59664E",
    "outline": "#607A50", "divider": "#D6DFC8", "yellow": "#F7E7AD",
    "ochre": "#71561F", "danger": "#9B453A", "danger_bg": "#F8E4DD",
}


def _stylesheet() -> str:
    css = """
    QWidget { color: @ink; font-family: "Microsoft YaHei UI", "Segoe UI"; font-size: 13px; }
    QWidget#TodoWindow { background: transparent; }
    QDialog, QMessageBox { background: @canvas; }
    QFrame#WindowShell { background: @canvas; border: 2px solid @outline; border-radius: 20px; }
    QFrame#SurfaceCard { background: @paper; border: 1px solid @divider; border-radius: 14px; }
    QWidget#TabBar { background: @soft; border-radius: 12px; }
    QLabel { background: transparent; border: none; }
    QLabel#AppTitle { font-size: 18px; font-weight: 700; }
    QLabel#PageTitle, QLabel#DialogTitle { font-size: 16px; font-weight: 700; }
    QLabel#SectionTitle { color: @primary; font-size: 12px; font-weight: 700; }
    QLabel#MutedText, QLabel#EmptyState { color: @muted; font-size: 12px; }
    QLabel#ErrorText { color: @danger; font-size: 12px; }
    QLabel#TaskText { font-size: 14px; }
    QLabel#TaskText[completed="true"] { color: @muted; }
    QLabel#FocusName { font-size: 15px; font-weight: 700; }
    QLabel#FocusTimer { color: @primary; font-family: "Consolas"; font-size: 42px; font-weight: 700; }
    QLabel#FocusTimer[compact="true"] { font-size: 36px; }
    QLabel#RecordDuration { color: @primary; font-family: "Consolas"; font-size: 17px; font-weight: 700; }
    QLineEdit, QDateEdit { background: @paper; color: @ink; border: 1px solid @outline; border-radius: 10px; padding: 5px 8px; min-height: 24px; selection-background-color: @primary; selection-color: @paper; }
    QLineEdit:focus, QDateEdit:focus { border: 2px solid @primary; padding: 4px 7px; }
    QLineEdit[invalid="true"] { border-color: @danger; }
    QDateEdit::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border: none; }
    QDateEdit::down-arrow { image: url(@chevron); width: 14px; height: 14px; }
    QCheckBox { spacing: 6px; min-height: 28px; }
    QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid @outline; border-radius: 6px; background: @paper; }
    QCheckBox::indicator:checked { background: @primary; border-color: @primary; image: url(@check); }
    QCheckBox::indicator:hover { border-color: @primary; background: @soft; }
    QCheckBox::indicator:checked:hover { background: @hover; }
    QCheckBox:focus { background: @soft; border-radius: 6px; }
    QToolButton, QPushButton { background: @soft; color: @ink; border: 1px solid transparent; border-radius: 9px; padding: 4px 8px; min-height: 22px; }
    QToolButton:hover, QPushButton:hover { background: @divider; }
    QToolButton:pressed, QPushButton:pressed { background: @accent; }
    QToolButton:focus, QPushButton:focus { border: 1px solid @primary; }
    QToolButton:disabled, QPushButton:disabled { color: @muted; background: @soft; }
    QToolButton#IconButton, QToolButton#DangerButton { background: transparent; padding: 0; }
    QToolButton#IconButton:hover { background: @soft; }
    QToolButton#DangerButton:hover, QToolButton#DangerButton:focus { background: @danger_bg; border-color: @danger; }
    QToolButton#PrimaryButton, QPushButton#PrimaryButton { background: @primary; color: @paper; border: 1px solid @pressed; border-bottom: 3px solid @pressed; font-weight: 700; }
    QToolButton#PrimaryButton:hover, QPushButton#PrimaryButton:hover { background: @hover; }
    QToolButton#PrimaryButton:pressed, QPushButton#PrimaryButton:pressed { background: @pressed; border-bottom-width: 1px; }
    QToolButton#PrimaryButton:focus, QPushButton#PrimaryButton:focus { border: 2px solid @ochre; }
    QToolButton#StopButton { background: @paper; border: 1px solid @outline; }
    QToolButton#StopButton:hover { background: @soft; }
    QToolButton::menu-indicator { image: none; }
    QToolButton#TabButton { background: transparent; font-weight: 700; padding: 2px 10px; border-radius: 9px; }
    QToolButton#TabButton:hover { background: @divider; }
    QToolButton#TabButton:checked { color: @paper; background: @primary; }
    QToolButton#TabButton:focus { border: 1px solid @ochre; }
    QToolButton#ImportantButton { color: @ochre; background: @paper; border: 1px solid @divider; }
    QToolButton#ImportantButton:checked { background: @yellow; border-color: @ochre; }
    QToolButton#ImportantButton:focus { border-color: @primary; }
    QPushButton#GroupToggleButton { background: @soft; color: @muted; font-size: 11px; padding: 0 6px; min-height: 22px; }
    QListWidget { background: transparent; border: none; outline: none; selection-background-color: @soft; }
    QListWidget::item { border: 1px solid transparent; border-radius: 8px; }
    QListWidget::item:hover { background: @soft; }
    QListWidget::item:selected { background: @soft; border-color: @outline; }
    QListWidget:focus { border: 1px solid @divider; border-radius: 8px; }
    QListWidget::drop-indicator { background: @primary; height: 2px; }
    QScrollBar:vertical { background: @canvas; width: 8px; border-radius: 4px; margin: 0; }
    QScrollBar::handle:vertical { background: @outline; min-height: 24px; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: @primary; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
    QMenu { background: @paper; border: 1px solid @outline; padding: 6px; }
    QMenu::item { padding: 7px 22px; border-radius: 6px; }
    QMenu::item:selected { background: @soft; }
    QMenu::separator { height: 1px; background: @divider; margin: 4px; }
    QToolTip { background: @paper; color: @ink; border: 1px solid @outline; padding: 5px; }
    QCalendarWidget QWidget { background: @paper; color: @ink; }
    QCalendarWidget QToolButton { background: @soft; color: @ink; }
    QCalendarWidget QAbstractItemView { background: @paper; color: @ink; selection-background-color: @primary; selection-color: @paper; }
    """
    for key in sorted(COLORS, key=len, reverse=True):
        css = css.replace(f"@{key}", COLORS[key])
    for name, filename in (("check", "check-white"), ("chevron", "chevron")):
        css = css.replace(f"@{name}", resource_path(f"assets/ui/{filename}.svg").as_posix())
    return css


WINDOW_CSS = _stylesheet()


def apply_theme(app) -> None:
    """Match native calendar/placeholder colors even on a dark Windows desktop."""
    from PySide6.QtGui import QColor, QPalette

    app.setStyle("Fusion")
    palette = QPalette()
    for role, color in {
        QPalette.Window: "canvas", QPalette.WindowText: "ink",
        QPalette.Base: "paper", QPalette.AlternateBase: "soft",
        QPalette.Text: "ink", QPalette.Button: "soft", QPalette.ButtonText: "ink",
        QPalette.Highlight: "primary", QPalette.HighlightedText: "paper",
        QPalette.ToolTipBase: "paper", QPalette.ToolTipText: "ink",
        QPalette.PlaceholderText: "muted",
    }.items():
        palette.setColor(role, QColor(COLORS[color]))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(COLORS["muted"]))
    app.setPalette(palette)
    app.setStyleSheet(WINDOW_CSS)
