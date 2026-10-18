# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter
import tkinterdnd2

# FFmpeg binaries are bundled from libs\ (see BUILD_INSTRUCTIONS.md).
# ffmpeg.exe must be a "full" build - the "essentials" build has no HAP encoder.
ffmpeg_path = os.path.join('libs', 'ffmpeg.exe')
ffprobe_path = os.path.join('libs', 'ffprobe.exe')
for path in (ffmpeg_path, ffprobe_path):
    if not os.path.exists(path):
        raise SystemExit(f"Missing {path} - see BUILD_INSTRUCTIONS.md")

a = Analysis(
    ['desktop_app\\main_gui.py'],
    pathex=[],
    binaries=[(ffmpeg_path, '.'), (ffprobe_path, '.')],
    datas=[
        (os.path.dirname(customtkinter.__file__), 'customtkinter/'),
        (os.path.dirname(tkinterdnd2.__file__), 'tkinterdnd2/'),
        ('assets', 'assets')
    ],
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
    icon='assets\\icon.ico',
)
