# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# ----------------------------------------------------------------------------
# USER CONFIGURATION REQUIRED:
# ----------------------------------------------------------------------------
# 1. Download static builds of ffmpeg and ffprobe for macOS (Intel or Apple Silicon).
# 2. Place them in a "libs" folder in this project root, OR update the paths below.
# ----------------------------------------------------------------------------

ffmpeg_path = './libs/ffmpeg'    # Path to your ffmpeg binary
ffprobe_path = './libs/ffprobe'  # Path to your ffprobe binary

# Verify files exist
if not os.path.exists(ffmpeg_path) or not os.path.exists(ffprobe_path):
    print("WARNING: ffmpeg or ffprobe binaries not found at configured paths.")
    print("Please download them and place in 'libs/' folder or update Oopl-Mac.spec")
    # We continue, but build might fail or result in broken app if binaries are missing
    binaries_list = []
else:
    binaries_list = [(ffmpeg_path, '.'), (ffprobe_path, '.')]

# ----------------------------------------------------------------------------

datas = []
datas += collect_data_files('customtkinter')
datas += collect_data_files('tkinterdnd2')

a = Analysis(
    ['desktop_app/main_gui.py'],
    pathex=[],
    binaries=binaries_list,
    datas=datas,
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
    [],
    exclude_binaries=True,
    name='Oopl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='Oopl',
)

app = BUNDLE(
    coll,
    name='Oopl.app',
    icon=None,
    bundle_identifier='com.antigravity.oopl',
)
