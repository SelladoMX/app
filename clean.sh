#!/bin/bash
# Clean script for SelladoMX
# Removes all build artifacts and caches

set -e

echo "=========================================="
echo "Cleaning SelladoMX build artifacts"
echo "=========================================="

# Clean build directories
echo "Cleaning build and dist directories..."
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

# Clean pytest cache
echo "Cleaning pytest cache..."
rm -rf .pytest_cache 2>/dev/null || true

# Clean eggs and wheels
echo "Cleaning eggs and wheels..."
rm -rf *.egg-info .eggs 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "✓ All build artifacts and caches cleaned!"
echo ""
echo "Now you can run: ./build.sh"
echo "=========================================="
