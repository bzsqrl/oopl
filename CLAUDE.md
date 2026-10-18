# Oopl

Desktop app (Windows + macOS) that turns video clips into seamless crossfaded VJ loops. Python + CustomTkinter + tkinterdnd2 GUI wrapping FFmpeg; packaged with PyInstaller.

## Layout
- `desktop_app/main_gui.py` — the whole GUI (`App` class). Entry point.
- `desktop_app/processor.py` — builds and runs the FFmpeg command (`process_video_crossfade`, `get_video_duration`).
- `Oopl.spec` (Windows, one-file `.exe`) / `Oopl-Mac.spec` (macOS, `.app` bundle).
- `libs/` — bundled `ffmpeg`/`ffprobe` binaries. **Gitignored**; must be set up per machine (see `BUILD_INSTRUCTIONS.md`).
- `USER_MANUAL.md` and `README.md` are the same document — keep them identical.

## Key facts
- `processor._find_binary` looks in `sys._MEIPASS` when frozen, `libs/` when run from source, then falls back to PATH. On macOS the binaries have no `.exe` suffix.
- **FFmpeg build matters.** "Essentials"/minimal builds lack the HAP encoder and HAP export fails with "Encoder not found". Always verify: `ffmpeg -hide_banner -encoders | grep -E ' (hap|dxv) '`. This bug shipped unnoticed in the Windows build from Mar–Oct 2026.
- FFmpeg's DXV encoder only supports `dxt1`, so DXV is fixed at "Normal" and the quality slider is disabled for it.
- Tk widgets must only be touched from the main thread. Background work (e.g. duration probing in `start_duration_probe`) returns results via `queue.Queue` polled with `after()`.
- There is no automated test suite. Verify changes by running `process_video_crossfade` against a synthetic clip (`ffmpeg -f lavfi -i testsrc=size=640x360:rate=30:duration=8 test.mp4`) for each format, then building and launching the app.

## Status / next up: macOS update (Oct 2026)
Windows work is done and pushed (HAP restored via a full FFmpeg build in `libs/`, DXV, per-file queue duration + remove button, legacy `backend/`/`cli.py`/`dev_scripts/` removed). `Oopl-Mac.spec` was updated from Windows but **not yet built or tested on a Mac**:
1. `pip install -r desktop_app/requirements.txt` (Python 3.10+).
2. Put macOS `ffmpeg` + `ffprobe` in `libs/`, `chmod +x`, and confirm `hap` and `dxv` encoders are present.
3. Run from source and test all formats (MP4, HAP, HAP Q, DXV, ProRes, MJPEG) with a synthetic clip.
4. `pyinstaller Oopl-Mac.spec` → `dist/Oopl.app`. Check: app launches, logo shows (assets now bundled), Dock icon uses `assets/icon.icns`, drag-and-drop works, HAP export works from the bundled app.
5. Remove this section once the Mac build is verified.
