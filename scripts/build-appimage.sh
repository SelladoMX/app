#!/bin/bash
set -e

echo "Building AppImage for SelladoMX..."

# Check required files exist
if [ ! -d "dist/SelladoMX" ]; then
    echo "Error: dist/SelladoMX directory not found. Run PyInstaller first."
    exit 1
fi

if [ ! -f "assets/selladomx.desktop" ]; then
    echo "Error: assets/selladomx.desktop not found"
    exit 1
fi

if [ ! -f "assets/selladomx.png" ]; then
    echo "Error: assets/selladomx.png not found"
    exit 1
fi

# Create AppDir structure
APPDIR="AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"

echo "Copying PyInstaller output to AppDir..."
# Copy the entire PyInstaller bundle
cp -r dist/SelladoMX/* "$APPDIR/usr/bin/"

# Copy desktop file and icon
cp assets/selladomx.desktop "$APPDIR/"
cp assets/selladomx.png "$APPDIR/selladomx.png"

# Make the executable actually executable
chmod +x "$APPDIR/usr/bin/SelladoMX"

# Set up environment variables for linuxdeploy Qt plugin
export QML_SOURCES_PATHS="$(pwd)/src"
export QMAKE=/usr/bin/qmake6  # Fallback, plugin will try to detect Qt6

echo "Running linuxdeploy to create AppImage..."

# Run linuxdeploy WITHOUT Qt plugin
# PyInstaller has already bundled all Qt libraries in _internal/
# We just need linuxdeploy to package everything into an AppImage
./linuxdeploy-x86_64.AppImage \
    --appdir "$APPDIR" \
    --executable "$APPDIR/usr/bin/SelladoMX" \
    --desktop-file "$APPDIR/selladomx.desktop" \
    --icon-file "assets/selladomx.png" \
    --output appimage

# Find the generated AppImage (linuxdeploy generates with a random-ish name)
GENERATED_APPIMAGE=$(ls -t SelladoMX*.AppImage 2>/dev/null | head -n1)

if [ -z "$GENERATED_APPIMAGE" ]; then
    echo "Error: AppImage was not generated"
    exit 1
fi

# Rename to our standard naming
FINAL_NAME="SelladoMX-Linux-x86_64.AppImage"
mv "$GENERATED_APPIMAGE" "dist/$FINAL_NAME"

echo "✓ AppImage created successfully: dist/$FINAL_NAME"
ls -lh "dist/$FINAL_NAME"

# Cleanup
rm -rf "$APPDIR"

echo "Done!"
