"""Make bundled PySide6 DLLs discoverable before Qt modules are imported."""

from __future__ import annotations

import os
import sys
from pathlib import Path


_DLL_DIRECTORY_HANDLES = []


def _register_bundle_dll_directories() -> None:
    if sys.platform != "win32" or not hasattr(sys, "_MEIPASS"):
        return

    bundle_root = Path(sys._MEIPASS)
    directories = [
        bundle_root / "PySide6",
        bundle_root / "shiboken6",
        bundle_root,
    ]
    existing = [directory for directory in directories if directory.is_dir()]

    add_dll_directory = getattr(os, "add_dll_directory", None)
    if add_dll_directory is not None:
        for directory in existing:
            try:
                _DLL_DIRECTORY_HANDLES.append(add_dll_directory(str(directory)))
            except OSError:
                pass

    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = os.pathsep.join(
        [*(str(directory) for directory in existing), old_path]
    )


_register_bundle_dll_directories()
