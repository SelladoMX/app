#!/bin/bash
# Build script for SelladoMX
# Creates executable for the current platform

set -e

# Change to project root directory
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Building SelladoMX for $(uname -s)"
echo "=========================================="

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed"
    echo "Install from: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    poetry install --with dev
fi

# Clean previous builds
echo "Cleaning previous builds..."
chmod -R u+w build dist 2>/dev/null || true
rm -rf build dist 2>/dev/null || true

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Clean PyInstaller cache
echo "Cleaning PyInstaller cache..."
rm -rf ~/.pyinstaller_cache 2>/dev/null || true

# Build with PyInstaller
echo "Building executable..."
poetry run pyinstaller selladomx.spec

# Platform-specific post-processing
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "✓ macOS build complete!"
    echo "Location: dist/SelladoMX.app"
    echo ""
    echo "To run: open dist/SelladoMX.app"
    echo "To create DMG: make dmg (or ./scripts/create-dmg.sh)"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    echo "✓ Linux build complete!"
    echo "Location: dist/selladomx/"
    echo ""
    echo "To run: ./dist/selladomx/selladomx"
    echo "To create archive: tar -czf SelladoMX-Linux.tar.gz -C dist selladomx"

elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo ""
    echo "✓ Windows build complete!"
    echo "Location: dist/selladomx/"
    echo ""
    echo "To run: dist\\selladomx\\selladomx.exe"
fi

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
