# Oopl Build Instructions for macOS

This guide explains how to run and build Oopl on macOS.

## Prerequisites

1.  **Python 3.10+**: Ensure Python is installed.
2.  **FFmpeg Binaries**: You need static binaries for `ffmpeg` and `ffprobe`.

## Setup

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

## Running from Source

1.  Install implicit dependencies if needed (usually handled by requirements).
2.  Run the app:
    ```bash
    python desktop_app/main_gui.py
    ```
    *Note: Ensure `ffmpeg` is reachable in your system PATH, or the app won't find it.*

## Building the .app Bundle

To create a standalone `Oopl.app`, we use PyInstaller.

### 1. Prepare Binaries
Unlike Windows where we assume a fixed path, for Mac you should place the `ffmpeg` and `ffprobe` binaries inside the project folder so they can be bundled.

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

### 2. Run Build
Use the provided Mac spec file:

```bash
pyinstaller Oopl-Mac.spec
```

### 3. Output
The built application will be in `dist/Oopl.app`.

## Troubleshooting

-   **"App is damaged" or Security Warning**: macOS often blocks unsigned apps. You may need to go to *System Settings > Privacy & Security* to allow it, or run:
    ```bash
    xattr -cr dist/Oopl.app
    ```
-   **TkinterDnD Issues**: If drag-and-drop fails, it's often because `tkinterdnd2` binaries are missing or incompatible. The `.spec` file attempts to collect them automatically.
