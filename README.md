# MacQRGenerator

A Python/Tkinter GUI for macOS to generate customizable QR codes.

## Requirements

- Python 3.8+
- [qrcode](https://pypi.org/project/qrcode/)
- [Pillow](https://pypi.org/project/Pillow/)

Install with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run in development

```bash
python qr_gui.py
```

## Build a standalone .app

We use PyInstaller:

```bash
pip install pyinstaller
# One-time: generate spec (already included here)
pyinstaller --windowed --name MacQRGenerator --icon icon.icns qr_gui.py

# Or reproducibly via the spec:
pyinstaller qr_gui.spec
```

The built app is in `dist/MacQRGenerator.app`. Double-click the `.app` to run.