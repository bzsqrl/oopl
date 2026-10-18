# Oopl User Manual

**Oopl** is a specialized tool for creating seamless VJ loops from video clips. It transforms any video segment into a perfect, infinite loop using advanced crossfading techniques.

Oopl runs on **Windows** and **macOS**. The app works the same on both; where something differs, this manual calls it out with **🪟 Windows** and **🍎 Mac** notes.

---

## 🚀 Getting Started

### System Requirements

| | 🪟 Windows | 🍎 Mac |
|---|---|---|
| **System** | Windows 10 or 11 (64-bit) | macOS 14 Sonoma or later |
| **Hardware** | Any 64-bit PC | Apple Silicon (M1 or later) |
| **Also needed** | Nothing | Rosetta 2 (see below) |

Oopl is fully **portable** and bundled with everything it needs, including FFmpeg. There is no installer.

### 🪟 Windows: Installing & Launching
1.  Copy `Oopl.exe` anywhere you like (e.g. your Desktop or a `Tools` folder).
2.  Double-click `Oopl.exe` to start.
    -   **"Windows protected your PC"**: Because Oopl is not code-signed, SmartScreen may warn you the first time. Click **More info → Run anyway**.
    -   The first launch can take a few seconds while Oopl unpacks itself.

### 🍎 Mac: Installing & Launching
1.  If you received a `.zip`, double-click it to extract `Oopl.app`.
2.  Drag `Oopl.app` into your **Applications** folder.
3.  **First launch only**: Because Oopl is not signed by Apple, macOS will block a normal double-click.
    -   Double-click `Oopl.app`, then dismiss the warning.
    -   Open **System Settings → Privacy & Security**, scroll down, and click **Open Anyway** next to the Oopl message.
    -   Confirm with **Open**. After this, Oopl launches normally.
4.  **Rosetta 2**: Oopl's video engine needs Apple's Rosetta 2. Most Macs already have it. If exports fail with *"Bad CPU type in executable"*, install it by opening **Terminal** and running:
    ```
    softwareupdate --install-rosetta --agree-to-license
    ```

> **✨ Quick Start**: Drag video files from **File Explorer** (Windows) or **Finder** (Mac) straight onto the Oopl window!

---

## 🖥 Interface Overview

The application is designed to be simple and vertical, consisting of four main sections (from top to bottom):

1.  **Settings**: Configure global parameters for the batch.
2.  **Queue**: Manage the list of files to process.
3.  **Process Control**: Start the operation.
4.  **Log**: View real-time progress and status.

---

## 🛠 Features Guide

### 1. Queue Management
You can batch process multiple videos at once. Use the **Queue** section to manage your inputs.

-   **Add Files**:
    -   Click **`+ Files`** to select specific video files.
    -   Click **`+ Folder`** to import all videos from a folder, including its subfolders.
    -   **Drag & Drop**: Drag files or folders onto the application window.
    -   *Supported Formats*: `.mp4`, `.mov`, `.avi`, `.mkv`.
-   **Selection**: Use the **checkboxes** next to each file to include or exclude them from the current batch.
-   **Duration**: Each file's length is shown to the right of its name.
-   **Remove**: Click the red **`X`** next to a file to remove just that file.
-   **Clear**: Click the **`Clear`** button (red) to remove all items from the list.

### 2. Settings & Configuration
Adjust how your loops are created.

#### Format
Choose the output video codec:
-   **MP4** (H.264): Standard, highly compatible.
-   **HAP**: GPU-accelerated codec for VJ software.
-   **DXV**: Resolume's native codec (DXV3 Normal Quality).
-   **ProRes**: Industry standard for editing and high quality.
-   **MJPEG**: Good balance of performance and quality.

Not sure which to pick? See **[Choosing a Format](#-choosing-a-format)** below.

#### Quality
Control output file size and visual fidelity. The slider adapts based on your selected Format:
-   **MP4**: Controls **CRF** (Constant Rate Factor). Range: 18 (Best) to 35 (Low).
-   **MJPEG**: Controls **Q** (Quantization). Range: 2 (Best) to 31 (Low).
-   **ProRes**: Selects Profile: **Proxy, LT, Standard, HQ**.
-   **HAP**: Selects Format: **Hap** or **Hap Q** (Higher Quality).
-   **DXV**: Fixed at **Normal** (DXT1, no alpha). This is the only DXV mode FFmpeg can encode, so the slider is disabled.
> **Visual Rule**: Moving the slider to the **Right** always improves quality (and likely increases file size).

#### Set Start (Trimming Input)
Ignore the beginning of a video clip (e.g., to skip an intro or unstable camera move).
-   **Enable**: Check "Set Start".
-   **Adjust**: Use the slider (0-60s, 0.5s steps) to seek into the video.
-   **Precise Input**: Click the number label (e.g., "0.0s"), type an exact value, and press **Enter** (🪟) / **Return** (🍎).

#### Crossfade
-   **Enable/Disable**: Toggle the checkbox to turn crossfading on or off.
-   **Duration**: Set blend time (0.5s to 31.5s).
-   **Precise Input**: Click the label to type exact seconds (up to 60s, FFmpeg's crossfade limit).
-   *Tip*: A 1.0s crossfade is usually sufficient for smooth loops.

#### Set Length (Trimming Output)
Define the exact duration of your final loop.
-   **Enable**: Check "Set Length".
-   **Adjust**: Use the slider (1s to 32s, 0.5s steps).
-   **Precise Input**: Click the label to type an exact value.
-   **Smart Constraints**: The app ensures length is at least `Crossfade + 0.5s`.

#### Scale (Resolution)
Resize your output video.
-   **Enable**: Check "Scale".
-   **Presets**: Click **4K** (3840x2160), **1080** (1920x1080), or **720** (1280x720).
-   **Custom**: Manually type width and height into the text boxes.
-   *Note*: Scaling stretches to the exact size you enter. Keep the original aspect ratio to avoid distortion.

#### Filename
Customize the output file naming convention.
-   **Append** (Default): Adds text to the end. `video.mp4` → `video_oopl.mp4`
-   **Prepend**: Adds text to the beginning. `video.mp4` → `_ooplvideo.mp4`
-   **Custom Text**: Edit the text field to change the tag (default `"_oopl"`). For Prepend, ending the tag with a space or underscore (e.g. `oopl_`) keeps names readable.

#### Output Directory
Choose where processed files are saved.
-   **Output To...**: Click to choose a specific folder for all output files.
-   **Default**: If no folder is selected (displays "Same as Input"), output files are saved in the same folder as their corresponding input files.
-   **Reset**: Click the Reset button to revert to the default behavior.

> **💡 Pro Tip (Keyboard Control)**: Click on any slider to focus it, then use your **Left/Right Arrow Keys** for precise adjustments. This works the same on Windows and Mac.

### 3. Processing
1.  Ensure files are in the Queue and checked.
2.  Click **Start Batch**.
3.  Monitor the **Log** area for progress.

---

## 🎛 Choosing a Format

Pick the format based on where the loop will be played.

| Use case | Recommended format | 🪟 Windows | 🍎 Mac |
|---|---|---|---|
| **Resolume** (Avenue / Arena) | **DXV** or **HAP** | ✅ | ✅ |
| **VDMX** | **HAP** / **Hap Q** | — | ✅ |
| **MadMapper**, **TouchDesigner** | **HAP** / **Hap Q** | ✅ | ✅ |
| **Millumin** | **HAP** / **Hap Q** | — | ✅ |
| **Video editing** (Premiere, Final Cut, DaVinci Resolve) | **ProRes** | ✅ | ✅ (Final Cut is Mac-only) |
| **Sharing, web, social media, phones** | **MP4** | ✅ | ✅ |
| **Older or lightweight VJ software** | **MJPEG** | ✅ | ✅ |

-   **HAP / DXV** play back smoothly at high resolutions because the graphics card does the decoding. Files are large.
-   **Hap Q** looks noticeably better than plain Hap (fewer color bands in gradients) at roughly twice the file size.
-   **MP4** files are the smallest but are harder on the computer to play, especially when mixing several layers live.

### Previewing your loops
Built-in players can't open every format:

| Format | 🪟 Windows (Media Player / Photos) | 🍎 Mac (QuickTime / Quick Look) |
|---|---|---|
| MP4 | ✅ | ✅ |
| ProRes | ❌ (use VLC or your editor) | ✅ |
| MJPEG | ✅ | ✅ |
| HAP / DXV | ❌ | ❌ |

For HAP and DXV, preview the loop in your VJ software. The free **VLC** player can also play most of them on both platforms.

---

## 📂 Output
Processed files are saved based on your **Output Directory** setting:
-   **Same as Input (Default)**: Next to the original file.
-   **Custom Directory**: In the specific folder you chose.
-   **Naming**: `OriginalName` + your tag (e.g., `waterfall.mp4` → `waterfall_oopl.mov`).
-   **File type**: MP4 exports are `.mp4`. HAP, DXV, ProRes and MJPEG exports are `.mov`.
-   **⚠️ Overwriting**: If a file with the same name already exists, Oopl replaces it without asking. Change the tag or output folder to keep earlier versions.

---

## ❓ FAQ & Troubleshooting

**Q: Why does the window stop resizing?**
A: Oopl enforces a minimum size (500x550) to ensure all controls remain visible and usable.

**Q: My video is shorter than the requested length?**
A: The application will attempt to use the maximum available duration. If the video is too short for the requested crossfade, it may fail or produce a shorter loop.

**Q: A file I dropped didn't appear in the queue.**
A: Only `.mp4`, `.mov`, `.avi` and `.mkv` files are accepted. Convert other formats first.

**Q (🪟 Windows): Windows Defender / antivirus flagged or deleted Oopl.exe.**
A: Some antivirus tools are suspicious of unsigned, self-extracting apps. If you got Oopl from a trusted source, restore it from quarantine and add an exception for it.

**Q (🍎 Mac): "Oopl.app is damaged and can't be opened" or "cannot be opened because the developer cannot be verified".**
A: This is macOS blocking an unsigned app. Follow the **First launch** steps above (*Privacy & Security → Open Anyway*). If the "damaged" message persists, open **Terminal** and run the command below (adjust the path if Oopl isn't in Applications), then open Oopl again:
```
xattr -cr /Applications/Oopl.app
```

**Q (🍎 Mac): Exports fail immediately with "Bad CPU type in executable".**
A: Rosetta 2 is missing. Install it with `softwareupdate --install-rosetta --agree-to-license` in Terminal.

**Q (🍎 Mac): Will Oopl run on an Intel Mac?**
A: The current Mac release is built for Apple Silicon only. Intel Mac users can build their own copy from the source code (see `BUILD_INSTRUCTIONS.md`).

**Q (🍎 Mac): Oopl can't read files from my Desktop, Documents or an external drive.**
A: If macOS asked whether Oopl may access a folder and you clicked **Don't Allow**, re-enable it in **System Settings → Privacy & Security → Files and Folders**.

**Q: How do I build Oopl myself?**
A: See `BUILD_INSTRUCTIONS.md` in the source code for Windows and Mac build steps.
