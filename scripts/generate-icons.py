#!/usr/bin/env python3
"""
Generate platform-specific icons from source PNG.

Source: assets/icon.png (any size, will be squared and resized)
Output:
  - assets/selladomx.png   (256x256, Linux AppImage + QML in-app icon)
  - assets/selladomx.ico   (multi-size, Windows)
  - assets/selladomx.icns  (multi-size, macOS — requires iconutil on macOS)

Usage: python scripts/generate-icons.py
Requires: pillow (pip install pillow)
"""

import shutil
import subprocess
import sys
import platform
from pathlib import Path

from PIL import Image


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
SOURCE = ASSETS_DIR / "icon.png"


def make_square(img: Image.Image) -> Image.Image:
    """Pad image with transparency to make it square."""
    w, h = img.size
    if w == h:
        return img
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    offset_x = (side - w) // 2
    offset_y = (side - h) // 2
    square.paste(img, (offset_x, offset_y))
    return square


def generate_png(source_img: Image.Image) -> None:
    """Generate 256x256 PNG for Linux and QML."""
    resized = source_img.resize((256, 256), Image.Resampling.LANCZOS)
    out = ASSETS_DIR / "selladomx.png"
    resized.save(out, "PNG")
    print(f"  Created: {out.relative_to(ASSETS_DIR.parent)}")


def generate_ico(source_img: Image.Image) -> None:
    """Generate multi-size .ico for Windows."""
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    out = ASSETS_DIR / "selladomx.ico"
    source_img.save(out, format="ICO", sizes=sizes)
    print(f"  Created: {out.relative_to(ASSETS_DIR.parent)}")


def generate_icns(source_img: Image.Image) -> None:
    """Generate .icns for macOS using iconutil."""
    iconset_dir = ASSETS_DIR / "selladomx.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # macOS iconset requires these exact filenames
    specs = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for size, filename in specs:
        resized = source_img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset_dir / filename, "PNG")

    if platform.system() != "Darwin":
        print(f"  Not on macOS — iconset saved to {iconset_dir.name}/")
        print(
            f"  Run on macOS: iconutil -c icns {iconset_dir} -o assets/selladomx.icns"
        )
        return

    out = ASSETS_DIR / "selladomx.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(out)],
        capture_output=True,
        text=True,
    )
    shutil.rmtree(iconset_dir)

    if result.returncode == 0:
        print(f"  Created: {out.relative_to(ASSETS_DIR.parent)}")
    else:
        print(f"  iconutil failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if not SOURCE.exists():
        print(f"Source icon not found: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    img = Image.open(SOURCE).convert("RGBA")
    print(f"Source: {SOURCE.name} ({img.size[0]}x{img.size[1]})")

    img = make_square(img)
    print(f"Squared: {img.size[0]}x{img.size[1]}")

    print("\nGenerating icons:")
    generate_png(img)
    generate_ico(img)
    generate_icns(img)
    print("\nDone.")


if __name__ == "__main__":
    main()
