# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_main.py'],
    pathex=[],
    binaries=[],
    datas=[('frontend', 'frontend'), ('backend', 'backend')],
    hiddenimports=['uvicorn', 'uvicorn.config', 'uvicorn.server', 'fastapi', 'starlette', 'pydantic', 'backend.server', 'backend.marker_core'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoMarker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoMarker',
)
