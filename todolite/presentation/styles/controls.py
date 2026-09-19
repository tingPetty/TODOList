"""Shared native control details not expressible through QSS."""
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import QCalendarWidget

from .theme import COLORS


def style_date_picker(picker) -> None:
    calendar = picker.calendarWidget()
    calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
    weekend = QTextCharFormat()
    weekend.setForeground(QColor(COLORS["muted"]))
    for day in (Qt.Saturday, Qt.Sunday):
        calendar.setWeekdayTextFormat(day, weekend)
    today = QTextCharFormat()
    today.setForeground(QColor(COLORS["primary"]))
    today.setBackground(QColor(COLORS["soft"]))
    today.setFontWeight(700)
    calendar.setDateTextFormat(QDate.currentDate(), today)
