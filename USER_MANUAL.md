# Oopl User Manual

**Oopl** is a specialized tool for creating seamless VJ loops from video clips. It transforms any video segment into a perfect, infinite loop using advanced crossfading techniques.

---

## 🚀 Getting Started

### Installation
Oopl is fully **portable** and bundled with all necessary dependencies (including FFmpeg). 
1.  Locate `Oopl.exe` (typically in the `dist` folder).
2.  That's it! No installation wizard is required.

### Launching
Double-click `Oopl.exe` to start the application.

> **✨ Quick Start**: You can immediately start by dragging video files directly onto the Oopl window!

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
    -   Click **`+ Folder`** to import all videos from a directory (recursive).
    -   **Drag & Drop**: Simply drag files or folders directly onto the application window.
    -   *Supported Formats*: .mp4, .mov, .avi, .mkv, and most common video formats.
-   **Selection**: Use the **checkboxes** next to each file to include or exclude them from the current batch.
-   **Clear**: Click the **`Clear`** button (red) to remove all items from the list.

### 2. Settings & Configuration
Adjust how your loops are created.

#### Format
Choose the output video codec:
-   **MP4** (H.264): Standard, highly compatible.
-   **HAP**: Integrity-optimized codec for VJ software (Resolume, VDMX).
-   **ProRes**: Industry standard for editing and high quality.
-   **MJPEG**: Good balance of performance and quality.

#### Quality (New!)
Control output file size and visual fidelity. The slider adapts based on your selected Format:
-   **MP4**: Controls **CRF** (Constant Rate Factor). Range: 18 (Best) to 35 (Low).
-   **MJPEG**: Controls **Q** (Quantization). Range: 2 (Best) to 31 (Low).
-   **ProRes**: Selects Profile: **Proxy, LT, Standard, HQ**.
-   **HAP**: Selects Format: **Hap** or **Hap Q** (Higher Quality).
> **Visual Rule**: Moving the slider to the **Right** always improves quality (and likely increases file size).

#### Crossfade
-   **Enable/Disable**: Toggle the checkbox to turn crossfading on or off.
-   **Duration**: Use the slider to set the blend time (0.1s to 10.0s).
-   *Tip*: A 1.0s crossfade is usually sufficient for smooth loops.

#### Set Start (Trimming Input)
Ignore the beginning of a video clip (e.g., to skip an intro or unstable camera move).
-   **How**: Check "Set Start" and adjust the slider.
-   **Effect**: The processed video will effectively "start" from this timestamp.

#### Set Length (Trimming Output)
Define the exact duration of your final loop.
-   **How**: Check "Set Length" and adjust the slider.
-   **Precision**:
    -   **0-10s**: Fine adjustments (0.1s steps).
    -   **10s+**: Coarse adjustments (1.0s steps).
-   **Smart Constraints**: The app ensures length >= crossfade duration + 0.5s.

#### Filename
Customize the output file naming convention.
-   **Append** (Default): Adds text to the end. `video.mp4` -> `video_oopl.mp4`
-   **Prepend**: Adds text to the beginning. `video.mp4` -> `_oopl video.mp4`
-   **Custom Text**: Edit the text field to change the tag (default `"_oopl"`).

#### Output Directory
Choose where processed files are saved.
-   **Output To...**: Click to choose a specific folder for all output files.
-   **Default**: If no folder is selected (displays "Same as Input"), output files are saved in the same folder as their corresponding input files.
-   **Reset**: Click the Reset button to revert to the default behavior.

> **💡 Pro Tip (Keyboard Control)**: Click on any slider to focus it, then use your **Left/Right Arrow Keys** for precise adjustments.

### 3. Processing
1.  Ensure files are in the Queue and checked.
2.  Click **Start Batch**.
3.  Monitor the **Log** area for progress.

---

## 📂 Output
Processed files are saved based on your **Output Directory** setting:
-   **Same as Input (Default)**: Next to the original file.
-   **Custom Directory**: In the specific folder you chose.
-   **Naming**: `OriginalName{Suffix}.{ext}` (e.g., `waterfall loop.mov`).

---

## ❓ FAQ

**Q: Why does the window stop resizing?**
A: Oopl enforces a minimum size (500x600) to ensure all controls remain visible and usable.

**Q: Can I run it on Mac?**
A: This version (`.exe`) is for Windows only. (Mac executable pending build).

**Q: My video is shorter than the requested length?**
A: The application will attempt to use the maximum available duration. If the video is too short for the requested crossfade, it may fail or produce a shorter loop.
