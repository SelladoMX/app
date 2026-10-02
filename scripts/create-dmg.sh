#!/bin/bash
# Create a DMG installer for macOS
# Requires Homebrew (installs create-dmg if missing)

set -e

cd "$(dirname "$0")/.."

if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script only works on macOS"
    exit 1
fi

if [ ! -d "dist/SelladoMX.app" ]; then
    echo "Error: SelladoMX.app not found. Run 'make build' first"
    exit 1
fi

echo "Creating DMG installer for macOS..."

if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

rm -f dist/SelladoMX-macOS.dmg

create-dmg \
  --volname "SelladoMX" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "SelladoMX.app" 200 190 \
  --hide-extension "SelladoMX.app" \
  --app-drop-link 600 185 \
  --no-internet-enable \
  "dist/SelladoMX-macOS.dmg" \
  "dist/SelladoMX.app" \
  || {
    echo "create-dmg failed, creating simple DMG..."
    hdiutil create -volname "SelladoMX" \
      -srcfolder "dist/SelladoMX.app" \
      -ov -format UDZO \
      "dist/SelladoMX-macOS.dmg"
  }

echo ""
echo "✓ DMG created: dist/SelladoMX-macOS.dmg"
echo ""
echo "To test: open dist/SelladoMX-macOS.dmg"
