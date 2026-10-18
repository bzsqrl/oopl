# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# ----------------------------------------------------------------------------
# USER CONFIGURATION REQUIRED:
# ----------------------------------------------------------------------------
# 1. Download static builds of ffmpeg and ffprobe for macOS (Intel or Apple Silicon).
#    ffmpeg must include the HAP encoder - check with: ./libs/ffmpeg -encoders | grep hap
# 2. Place them in a "libs" folder in this project root, OR update the paths below.
# ----------------------------------------------------------------------------

ffmpeg_path = './libs/ffmpeg'    # Path to your ffmpeg binary
ffprobe_path = './libs/ffprobe'  # Path to your ffprobe binary

# Verify files exist - a build without them produces an app that cannot export
for path in (ffmpeg_path, ffprobe_path):
    if not os.path.exists(path):
        raise SystemExit(f"Missing {path} - see BUILD_INSTRUCTIONS.md")
binaries_list = [(ffmpeg_path, '.'), (ffprobe_path, '.')]

# ----------------------------------------------------------------------------

datas = []
datas += collect_data_files('customtkinter')
datas += collect_data_files('tkinterdnd2')
datas += [('assets', 'assets')] # In-app logo

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
    icon='assets/icon.icns',
    bundle_identifier='com.antigravity.oopl',
)
