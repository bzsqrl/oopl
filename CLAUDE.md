# Oopl

Desktop app (Windows + macOS) that turns video clips into seamless crossfaded VJ loops. Python + CustomTkinter + tkinterdnd2 GUI wrapping FFmpeg; packaged with PyInstaller.

## Layout
- `desktop_app/main_gui.py` — the whole GUI (`App` class). Entry point.
- `desktop_app/processor.py` — builds and runs the FFmpeg command (`process_video_crossfade`, `get_video_duration`).
- `Oopl.spec` (Windows, one-file `.exe`) / `Oopl-Mac.spec` (macOS, `.app` bundle).
- `libs/` — bundled `ffmpeg`/`ffprobe` binaries. **Gitignored**; must be set up per machine (see `BUILD_INSTRUCTIONS.md`).
- `USER_MANUAL.md` and `README.md` are the same document — keep them identical.

## Key facts
- `processor._find_binary` looks in `sys._MEIPASS` when frozen, `libs/` when run from source, then falls back to PATH. On macOS the binaries have no `.exe` suffix. The Mac spec bundles them into `bin/`: a bare `ffmpeg` file at the bundle root shadows the `ffmpeg` (ffmpeg-python) package and the app crashes on launch with a circular-import error.
- **FFmpeg build matters.** "Essentials"/minimal builds lack the HAP encoder and HAP export fails with "Encoder not found". Always verify: `ffmpeg -hide_banner -encoders | grep -E ' (hap|dxv) '`. This bug shipped unnoticed in the Windows build from Mar–Oct 2026.
- FFmpeg's DXV encoder only supports `dxt1`, so DXV is fixed at "Normal" and the quality slider is disabled for it.
- Tk widgets must only be touched from the main thread. Background work (e.g. duration probing in `start_duration_probe`) returns results via `queue.Queue` polled with `after()`.
- There is no automated test suite. Verify changes by running `process_video_crossfade` against a synthetic clip (`ffmpeg -f lavfi -i testsrc=size=640x360:rate=30:duration=8 test.mp4`) for each format, then building and launching the app.
