# Assets

## Icons

- `icon.png` - Source icon

Regenerate the platform icons from `icon.png` with `python scripts/generate-icons.py` (requires Pillow; `.icns` requires `iconutil` on macOS):

- `selladomx.png` - 256x256, Linux (Flatpak) and in-app QML icon
- `selladomx.ico` - Windows icon (multi-size)
- `selladomx.icns` - macOS icon bundle (multi-size)

## Desktop Entry
- `selladomx.desktop` - Linux desktop entry; the Flatpak manifest installs it as `com.selladomx.SelladoMX.desktop`

## Documentation
- `README-Windows.txt` - Copied into the Windows build as `README.txt`
