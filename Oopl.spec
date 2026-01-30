# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop_app\\main_gui.py'],
    pathex=[],
    binaries=[('C:\\ffmpeg\\ffmpeg.exe', '.'), ('C:\\ffmpeg\\ffprobe.exe', '.')],
    datas=[('c:\\users\\beatf\\appdata\\local\\programs\\python\\python310\\lib\\site-packages\\customtkinter', 'customtkinter/'), ('c:\\users\\beatf\\appdata\\local\\programs\\python\\python310\\lib\\site-packages\\tkinterdnd2', 'tkinterdnd2/')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='Oopl',
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
)
