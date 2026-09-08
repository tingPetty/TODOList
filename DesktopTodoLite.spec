# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


a = Analysis(
    ['todolite/app/entrypoint.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['todolite/app/qt_runtime_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PyInstaller can discover an unrelated ICU pair from the developer runtime
# (for example Poppler's ICU 78). PySide6's Qt6Core on Windows uses the
# system ICU forwarder DLLs with unversioned exports, so keep those unrelated
# binaries out of the one-file bundle and let Windows resolve its own ICU.
system_icu_names = {"icuuc.dll", "icudt78.dll"}
binaries = [
    entry
    for entry in a.binaries
    if Path(entry[0]).name.lower() not in system_icu_names
]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    binaries,
    a.datas,
    [],
    name='DesktopTodoLite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'],
)
