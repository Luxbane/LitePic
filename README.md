# LitePic

A dead-simple, lightweight photo viewer for Windows. Built for old/weak hardware where Microsoft Photos lags — no cloud sync, no editing suite, no background bloat. Just open a photo and look at it.

## Why

Microsoft Photos is a heavy UWP app with a lot going on under the hood (cloud integration, telemetry, AI features) that isn't needed just to look at a picture. On weak hardware (this was built and tested on an Intel i3-5005U with 6GB RAM and integrated graphics), that overhead shows. LitePic is built with Tkinter (Python's built-in GUI toolkit) specifically because it has a tiny footprint compared to Qt/Electron-based alternatives — the goal is fast startup and low memory use, not a modern-looking UI.

## Features

- Double-click a photo to open it directly (works as your default photo viewer — see [Setting as default](#setting-litepic-as-your-default-photo-viewer))
- Next/previous navigation through the same folder (Left/Right arrow keys)
- Window automatically sizes to match the photo (capped to your screen size)
- Zoom (scroll wheel) and pan (click and drag)
- Rotate left/right, flip horizontal/vertical — lossless, no quality loss
- Crop, with a simple click-drag selection
- Undo/redo (Ctrl+Z / Ctrl+Y), up to 20 steps
- Save As (Ctrl+S) — always prompts for a filename/location, never silently overwrites your original photo
- File > Open (Ctrl+O) to browse for a photo manually

## Download

Grab the latest build from **[Releases](../../releases/latest)** — extract the zip and run `LitePic.exe`. No installer, no dependencies to set up.

## Setting LitePic as your default photo viewer

1. Right-click any photo → **Open with** → **Choose another app**
2. Browse to `LitePic.exe` if it's not already listed
3. Check **"Always use this app to open .jpg files"** (or whatever extension) → OK

**Note (Windows 11):** Microsoft removed the ability to set one app as default for *all* image types at once, so you'll need to repeat this per extension (.jpg, .jpeg, .png, .bmp, .gif, .webp). This is a Windows limitation, not something LitePic can work around.

The first time you point Windows at `LitePic.exe`, you may see a "Windows protected your PC" SmartScreen warning — this is expected for any unsigned app (a code-signing certificate costs money this project doesn't spend). Click **More info → Run anyway**.

## Building from source

Requirements: Python 3.11+ available as `py` on your PATH.

1. Clone this repo.
2. Run `Build.bat`.

This creates a virtual environment, installs Pillow + PyInstaller, and builds `dist/LitePic/LitePic.exe`.

## Controls

| Action | Shortcut |
|---|---|
| Next / previous photo | Right / Left arrow |
| Zoom | Mouse scroll wheel |
| Pan (when zoomed in) | Click and drag |
| Rotate right / left | Toolbar, or R / L |
| Flip horizontal / vertical | Toolbar, or H / V |
| Crop | Toolbar → Crop, drag to select, Save/Cancel |
| Undo / Redo | Ctrl+Z / Ctrl+Y |
| Save As | Ctrl+S, or toolbar |
| Open a photo | Ctrl+O, or File > Open |

## License

MIT — see [`LICENSE`](./LICENSE).
