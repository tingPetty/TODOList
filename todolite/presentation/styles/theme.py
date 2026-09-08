"""Centralized QSS for the Todo and Focus pages."""

WINDOW_CSS = """
QWidget#TodoWindow {
    background: transparent;
}
QFrame#SurfaceCard {
    background: rgba(65, 82, 106, 224);
    border: 1px solid rgba(255, 255, 255, 34);
    border-radius: 18px;
}
QLabel#AppTitle {
    color: #f3f7fc;
    font-size: 18px;
    font-weight: 800;
}
QLabel#PageTitle {
    color: #f3f7fc;
    font-size: 16px;
    font-weight: 750;
}
QLabel#SectionTitle {
    color: #dbe8f7;
    font-size: 12px;
    font-weight: 750;
}
QLabel#MutedText {
    color: rgba(226, 232, 240, 166);
    font-size: 12px;
}
QLabel#TaskText {
    color: #e2e8f0;
    font-size: 14px;
}
QLabel#FocusTimer {
    color: #fff7d6;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 2px;
}
QLabel#FocusName {
    color: #f8fbff;
    font-size: 17px;
    font-weight: 700;
}
QLabel#EmptyState {
    color: rgba(226, 232, 240, 160);
    font-size: 13px;
    padding: 20px 8px;
}
QLineEdit, QDateEdit {
    background: rgba(255, 255, 255, 28);
    border: 1px solid rgba(255, 255, 255, 56);
    border-radius: 10px;
    color: #f8fafc;
    padding: 7px 9px;
    min-height: 20px;
}
QLineEdit:focus, QDateEdit:focus {
    border: 1px solid rgba(186, 230, 253, 150);
    background: rgba(255, 255, 255, 38);
}
QCheckBox {
    color: #e2e8f0;
    font-size: 13px;
    spacing: 7px;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid rgba(226, 232, 240, 140);
    border-radius: 4px;
    background: rgba(15, 23, 42, 110);
}
QCheckBox::indicator:checked {
    background: rgba(74, 222, 128, 190);
    border: 1px solid rgba(134, 239, 172, 220);
}
QToolButton#IconButton {
    color: #e7f0fb;
    background: rgba(255, 255, 255, 18);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
}
QToolButton#IconButton:hover {
    background: rgba(255, 255, 255, 48);
}
QToolButton#IconButton:pressed {
    background: rgba(125, 211, 252, 75);
}
QToolButton#DangerButton {
    color: #fecdd3;
    background: rgba(248, 113, 113, 24);
    border-color: rgba(248, 113, 113, 45);
}
QToolButton#DangerButton:hover {
    color: #fff1f2;
    background: rgba(248, 113, 113, 76);
}
QToolButton#PrimaryButton {
    color: #082f49;
    background: #a7f3d0;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 800;
}
QToolButton#PrimaryButton:hover {
    background: #bbf7d0;
}
QToolButton#StopButton {
    color: #fff1f2;
    background: rgba(248, 113, 113, 190);
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 800;
}
QToolButton#StopButton:hover {
    background: rgba(239, 68, 68, 220);
}
QToolButton#TabButton {
    color: rgba(226, 232, 240, 170);
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 16px;
}
QToolButton#TabButton:hover {
    color: #f8fafc;
    background: rgba(255, 255, 255, 24);
}
QToolButton#TabButton:checked {
    color: #fef3c7;
    background: rgba(253, 230, 138, 28);
    border-bottom: 2px solid #fcd34d;
}
QPushButton#GroupToggleButton {
    color: rgba(226, 232, 240, 200);
    background: rgba(30, 41, 59, 70);
    border: none;
    border-radius: 8px;
    padding: 3px 8px;
}
QPushButton#GroupToggleButton:hover {
    background: rgba(148, 163, 184, 85);
}
QListWidget#TaskList, QListWidget#RecordList {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget#TaskList::item, QListWidget#RecordList::item {
    background: transparent;
    border: none;
}
QMenu {
    background: rgba(17, 24, 39, 245);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 35);
}
QMenu::item:selected {
    background: rgba(148, 163, 184, 70);
}
/* Light utility dialogs use dark text so labels remain readable on their
   native light background. Cards inside the dialogs keep the shared dark
   card styling above. */
QDialog#LightDialog {
    background: #f8fafc;
    color: #334155;
}
QDialog#LightDialog QLabel {
    color: #334155;
}
QDialog#LightDialog QLabel#PageTitle {
    color: #0f172a;
}
QDialog#LightDialog QLabel#SectionTitle {
    color: #334155;
}
QDialog#LightDialog QLabel#MutedText {
    color: #64748b;
}
QDialog#LightDialog QLineEdit,
QDialog#LightDialog QDateEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #1e293b;
}
QDialog#LightDialog QLineEdit:focus,
QDialog#LightDialog QDateEdit:focus {
    background: #ffffff;
    border: 1px solid #60a5fa;
}
QDialog#LightDialog QCheckBox {
    color: #334155;
}
QDialog#LightDialog QDialogButtonBox QPushButton {
    color: #1e293b;
}
"""
