# Desktop Todo Lite

A lightweight Windows desktop Todo and focus widget built with PySide6.

## Features

- Semi-transparent floating window
- Compact default window layout with a draggable bottom-right resize handle
- Two top-level pages switched by the `Todo` and `专注` tabs
- Add tasks by pressing Enter
- Add tasks with selectable date (default today)
- Mark tasks as important (bold + exclamation marker)
- Check task to strike through (only checkbox click toggles completion)
- Delete task manually
- Double-click task text to edit text/date/important in one dialog
- Drag to reorder active tasks
- Drag active tasks across date groups and auto-sync task date
- Completed tasks sink to bottom automatically
- Group tasks by date
- Collapse completed tasks per date group
- Hide completed tasks from 2+ days ago in the main list (display only)
- Auto-clean completed history older than 30 days from storage (Beijing time, by task date)
- Task statistics panel (30-day completion curve + per-day completed list)
- Focus page with named forward timer, pause/resume, finish, and history
- Focus history retained for the latest seven calendar days by default
- Local JSON persistence
- Per-date collapse state persistence across app restarts
- Startup toggle (Windows)

## Quick Start

1. Double-click `DesktopTodoLite.exe` in the project root.

The executable is the only supported user-facing launch method. The application stores its data in the `.data/` directory beside the executable.

Enable “开机自启” from the in-app menu when you want Windows to launch the same executable after sign-in.

## Build for maintainers

Install the build dependencies from `requirements.txt`, then run PyInstaller from the project environment:

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --distpath . DesktopTodoLite.spec
```

This produces `DesktopTodoLite.exe` in the project root. The spec uses the internal `todolite/app/entrypoint.py` and embeds the icon/assets for the windowed one-file build.

## Notes

- Source runs store data under `./.data/`; packaged exe runs store data in `.data/` beside the exe.
- Todo data is stored in `.data/tasks.json`; settings are stored in `.data/settings.json`.
- Focus history is stored in `.data/focus_sessions.json`; recoverable active focus state is stored in `.data/focus_state.json`.
- Startup uses `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`.
- When the app starts with autostart enabled, it repairs a missing or stale startup command automatically; source runs use `pythonw.exe` when available so no console window is opened.
- The SVG/ICO icon is applied to the QApplication, the main window, the Windows AppUserModelID, and the PyInstaller executable so manual and autostart launches use the same icon.
- The packaged executable registers its bundled PySide6, shiboken6, and Qt DLL directories before importing Qt, so it can run from Explorer or Windows autostart without inheriting the development environment PATH.
- The project no longer uses a BAT/conda launcher; the executable is the only user-facing launch entry.
- Display rule: in the main list, completed tasks with `task_date <= (today in UTC+8 - 2 days)` are hidden (not deleted).
- Retention rule: completed records with `task_date < (today in UTC+8 - 29 days)` are removed from storage on refresh/save.
- Focus rule: completed focus records older than the latest seven Beijing calendar dates are removed on startup and after a new session finishes.
- The default window size is `430x420`, the minimum size is `360x360`, and dragging the lower-right grip resizes both dimensions.
- The code is organized into `domain`, `services`, `infrastructure`, and `presentation` layers; Todo and Focus use shared presentation components.
