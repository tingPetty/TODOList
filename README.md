# Desktop Todo Lite

A lightweight Windows desktop todo widget built with PySide6.

## Features

- Semi-transparent floating window
- Add tasks by pressing Enter
- Add tasks with selectable date (default today)
- Mark tasks as important (bold + exclamation marker)
- Check task to strike through (only checkbox click toggles completion)
- Delete task manually
- Double-click task text to edit text/date/important in one dialog
- Drag to reorder active tasks
- Completed tasks sink to bottom automatically
- Group tasks by date
- Collapse completed tasks per date group
- Local JSON persistence
- Per-date collapse state persistence across app restarts
- Startup toggle (Windows)

## Quick Start

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run:

```powershell
python main.py
```

3. One-click launch on Windows:

- Double-click `start_todo.bat` to run with conda env `todo_desk`.

## Build (optional)

```powershell
pip install pyinstaller
pyinstaller --name DesktopTodoLite --windowed --onefile main.py
```

## Notes

- Data file and settings are stored in `./.data/` under project root.
- Startup uses `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`.
- Project launch script uses conda env `todo_desk` via `start_todo.bat`.
