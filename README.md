[繁體中文](README.zh-TW.md) | English

---

# PSD Layer to PNG Exporter

Export each layer from a `.psd` file as an individual `.png` file, preserving each layer's original position on the canvas.

## Features

- Browse and select any `.psd` or `.psb` file
- Custom output folder
- Custom filename prefix
- Optional auto-numbering (`01_`, `02_`, …) — enabled by default, toggleable
- Supports group layers with recursive export of child layers
- Each PNG matches the full canvas size with layer position intact (transparency preserved)
- Real-time export log
- 🌐 Language selection on first launch (English / 繁體中文), preference saved automatically

## Usage

### Option 1: Run the Python script directly

**Install dependencies:**
```bash
pip install psd-tools
```

**Run:**
```bash
python psd_to_png_gui.py
```

### Option 2: Build as a standalone .exe (Windows, no Python required)

**Install dependencies:**
```bash
pip install pyinstaller psd-tools
```

**Build:**
```bash
pyinstaller --onefile --windowed --name PSD-to-PNG psd_to_png_gui.py
```

The compiled `PSD-to-PNG.exe` will be in the `dist/` folder — ready to share with anyone, no Python installation needed.

## Download

Pre-built Windows executables are available on the [Releases](../../releases) page.

## Language

On first launch, a language selection dialog will appear. Your choice is saved to `config.json` in the same folder as the executable. To reset the language, simply delete `config.json`.

## Requirements

- Python 3.8 or higher
- Windows (GUI built with tkinter, included with Python)

## Dependencies

| Package | Purpose |
|---------|---------|
| psd-tools | Parse `.psd` files and layers |
| Pillow | Image processing (installed automatically with psd-tools) |
| pyinstaller | Build standalone executable (optional) |

## Changelog

### v1.1.0
- Added language selection dialog on first launch (English / 繁體中文)
- Language preference is saved and remembered across sessions

### v1.0.0
- Initial release
- Export PSD layers as individual PNG files
- Preserve original layer position on canvas
- Custom output folder, filename prefix, and auto-numbering