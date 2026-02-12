# Assets

This directory contains application resources and icons.

## Icons

### Source
- `icon.png` - Original icon downloaded from selladomx.com (280x268)

### Generated Icons
Run `poetry run python scripts/generate-icons.py` to regenerate:

- `icon.ico` - Windows icon (multi-size: 16x16 to 256x256)
- `icon.icns` - macOS icon bundle (all retina sizes)
- `icon-linux.png` - Linux icon (280x268)

### Legacy Icons
- `selladomx.png` - Old placeholder icon
- `selladomx.svg` - Old vector icon

## Desktop Entry
- `selladomx.desktop` - Linux desktop integration file

## Documentation
- `README-Windows.txt` - Windows-specific instructions (included in Windows builds)
