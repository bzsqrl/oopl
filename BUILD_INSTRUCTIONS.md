# Oopl Build Instructions

## Windows

Run all commands below from the **project root** (the folder containing `Oopl.spec`). The spec uses relative paths, so building from anywhere else fails.

### Prerequisites

1.  **Python 3.10+** (last built with 3.10.6), with "Add to PATH" enabled during install.
2.  **[7-Zip](https://www.7-zip.org/)**, needed to extract the full FFmpeg build (it's only published as `.7z`).

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

A virtual environment (`python -m venv venv`, then `venv\Scripts\activate`) is optional but keeps these packages separate from other projects.

### 2. Prepare FFmpeg Binaries

FFmpeg is bundled into the exe from a `libs` folder. `libs/` is gitignored (the binaries are large), so set it up on each machine:

1.  Download `ffmpeg-release-full.7z` from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and extract it with 7-Zip.
    > ⚠️ It must be the **full** build. The "essentials" build has **no HAP encoder**, and HAP export fails with "Encoder not found".
2.  Create `libs\` in the project root and copy in:
    - `bin\ffmpeg.exe` from the full build.
    - `ffprobe.exe`: any build works, since it only reads clip durations. The essentials `ffprobe.exe` (~100 MB) keeps the exe much smaller than the full one (~230 MB).
    - `LICENSE` from the full build, renamed to `FFMPEG-LICENSE.txt`.
3.  Confirm the encoders are present:
    ```powershell
    libs\ffmpeg.exe -hide_banner -encoders | findstr /R "hap dxv"
    ```
    Both `hap` and `dxv` should be listed.

### 3. Run from Source

```powershell
python desktop_app\main_gui.py
```

The app uses `libs\ffmpeg.exe` and `libs\ffprobe.exe` if present, otherwise falls back to `ffmpeg`/`ffprobe` on your PATH.

### 4. Build the .exe

```powershell
pyinstaller Oopl.spec
```

If `pyinstaller` isn't recognized, use `python -m PyInstaller Oopl.spec`. The build takes about a minute and stops with an error if `libs\` is missing a binary.

### 5. Output

- `dist\Oopl.exe`: a single portable file (~145 MB) with Python, the GUI libraries and FFmpeg inside. Rebuilding **overwrites** it, so rename the previous one first if you want to keep it.
- `build\` holds intermediate files and can be deleted.
- When distributing, put `Oopl.exe` and `FFMPEG-LICENSE.txt` together in a zip. FFmpeg is GPL-licensed and the license must accompany it.

### Troubleshooting

-   **"Windows protected your PC" (SmartScreen)**: the exe is unsigned. Click *More info → Run anyway*.
-   **Slow first launch**: the one-file exe unpacks itself to a temp folder on each launch, so a few seconds' delay is normal.
-   **HAP export fails with "Encoder not found"**: the bundled `ffmpeg.exe` is not a full build. Redo step 2 and rebuild.
-   **Build fails with "Missing libs\…"**: you're not in the project root, or `libs\` isn't set up (step 2).

---

## macOS

This section explains how to run and build Oopl on macOS.

### Prerequisites

1.  **Python 3.10+**: Ensure Python is installed.
2.  **FFmpeg Binaries**: You need static binaries for `ffmpeg` and `ffprobe`.

### Setup

1.  **Clone/Copy Repository**: Get the source code onto your Mac.
2.  **Create Virtual Environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `tkinterdnd2` and `customtkinter` should install without issues.*

### Running from Source

1.  Run the app:
    ```bash
    python desktop_app/main_gui.py
    ```
    *Note: The app uses `libs/ffmpeg` and `libs/ffprobe` if present (see below), otherwise falls back to `ffmpeg`/`ffprobe` on your PATH.*

### Building the .app Bundle

To create a standalone `Oopl.app`, we use PyInstaller.

#### 1. Prepare Binaries
As on Windows, place the `ffmpeg` and `ffprobe` binaries in a `libs` folder inside the project so they can be bundled.

1.  Create a folder named `libs` in the project root.
2.  Download macOS static builds for FFmpeg (e.g., from [evermeet.cx](https://evermeet.cx/ffmpeg/)).
3.  Extract `ffmpeg` and `ffprobe` executables into the `libs/` folder.
    - Structure should be:
      - `root/libs/ffmpeg`
      - `root/libs/ffprobe`
4.  Ensure they are executable:
    ```bash
    chmod +x libs/ffmpeg libs/ffprobe
    ```
5.  Confirm `ffmpeg` has the HAP encoder (some builds omit it, which silently breaks HAP export):
    ```bash
    ./libs/ffmpeg -hide_banner -encoders | grep -E ' (hap|dxv) '
    ```
    Both `hap` and `dxv` should be listed. If `hap` is missing, use a different build (or `brew install ffmpeg` and copy its binaries, noting Homebrew builds are dynamically linked and won't run on other Macs).

#### 2. Run Build
Use the provided Mac spec file:

```bash
pyinstaller Oopl-Mac.spec
```

#### 3. Output
The built application will be in `dist/Oopl.app`.

### Troubleshooting

-   **"App is damaged" or Security Warning**: macOS often blocks unsigned apps. You may need to go to *System Settings > Privacy & Security* to allow it, or run:
    ```bash
    xattr -cr dist/Oopl.app
    ```
-   **TkinterDnD Issues**: If drag-and-drop fails, it's often because `tkinterdnd2` binaries are missing or incompatible. The `.spec` file attempts to collect them automatically.
