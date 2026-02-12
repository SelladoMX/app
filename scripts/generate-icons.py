#!/usr/bin/env python3
"""
Generate platform-specific icons from source PNG
Requires: pip install pillow
"""
import sys
from pathlib import Path
from PIL import Image

def generate_icons():
    """Generate .ico for Windows and .icns for macOS from PNG"""

    source = Path("assets/icon.png")
    if not source.exists():
        print(f"❌ Source icon not found: {source}")
        sys.exit(1)

    print(f"📦 Loading source icon: {source}")
    img = Image.open(source)

    # Ensure RGBA mode
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    print(f"   Size: {img.size}")
    print(f"   Mode: {img.mode}")

    # Generate Windows .ico (multi-size)
    print("\n🪟 Generating Windows icon...")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for size in ico_sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        ico_images.append(resized)

    ico_path = Path("assets/icon.ico")
    ico_images[0].save(
        ico_path,
        format='ICO',
        sizes=ico_sizes,
        append_images=ico_images[1:]
    )
    print(f"   ✅ Created: {ico_path}")

    # Generate macOS .icns
    print("\n🍎 Generating macOS icon...")

    # Create iconset directory
    iconset_dir = Path("assets/icon.iconset")
    iconset_dir.mkdir(exist_ok=True)

    # macOS requires specific sizes
    icns_sizes = [
        (16, 16, "16x16"),
        (32, 32, "16x16@2x"),
        (32, 32, "32x32"),
        (64, 64, "32x32@2x"),
        (128, 128, "128x128"),
        (256, 256, "128x128@2x"),
        (256, 256, "256x256"),
        (512, 512, "256x256@2x"),
        (512, 512, "512x512"),
        (1024, 1024, "512x512@2x"),
    ]

    for width, height, name in icns_sizes:
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        output_path = iconset_dir / f"icon_{name}.png"
        resized.save(output_path, 'PNG')

    print(f"   📁 Created iconset: {iconset_dir}")

    # Convert to .icns using iconutil (macOS only)
    import subprocess
    import platform

    if platform.system() == 'Darwin':
        print("   🔧 Converting to .icns with iconutil...")
        result = subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', 'assets/icon.icns'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"   ✅ Created: assets/icon.icns")
            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
            print(f"   🧹 Cleaned up: {iconset_dir}")
        else:
            print(f"   ⚠️  iconutil failed: {result.stderr}")
            print(f"   💡 Keeping {iconset_dir} for manual conversion")
    else:
        print(f"   ⚠️  Not on macOS - keeping {iconset_dir} for manual conversion")
        print(f"   💡 On macOS, run: iconutil -c icns {iconset_dir} -o assets/icon.icns")

    # Copy PNG for Linux
    linux_icon = Path("assets/icon-linux.png")
    img.save(linux_icon, 'PNG')
    print(f"\n🐧 Linux icon: {linux_icon}")

    print("\n✅ Icon generation complete!")
    print("\nGenerated files:")
    print(f"  - assets/icon.png (source)")
    print(f"  - assets/icon.ico (Windows)")
    print(f"  - assets/icon.icns (macOS)")
    print(f"  - assets/icon-linux.png (Linux)")

if __name__ == '__main__':
    generate_icons()
