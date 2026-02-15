#!/bin/bash
# Build Flatpak locally for testing

set -e

MANIFEST="com.selladomx.SelladoMX.yml"
BUILD_DIR="build-flatpak"
REPO_DIR="flatpak-repo"

echo "Building SelladoMX Flatpak..."

# Ensure dependencies are generated
if [ ! -f "generated-sources.json" ]; then
    echo "Generando dependencias Python..."
    ./scripts/generate-python-deps.sh
fi

# Build
flatpak-builder --force-clean --ccache --repo="$REPO_DIR" "$BUILD_DIR" "$MANIFEST"

# Export bundle for testing
flatpak build-bundle "$REPO_DIR" SelladoMX-dev.flatpak com.selladomx.SelladoMX

echo "✓ Build completo: SelladoMX-dev.flatpak"
echo ""
echo "Para instalar localmente:"
echo "  flatpak install --user SelladoMX-dev.flatpak"
echo ""
echo "Para ejecutar:"
echo "  flatpak run com.selladomx.SelladoMX"
