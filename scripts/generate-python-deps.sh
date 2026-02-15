#!/bin/bash
# Genera dependencies JSON para Flatpak desde poetry.lock

set -e

echo "Generando dependencias Python para Flatpak..."

# Check if flatpak-builder-tools exists, if not clone it
if [ ! -d "flatpak-builder-tools" ]; then
    echo "Clonando flatpak-builder-tools..."
    git clone --depth 1 https://github.com/flatpak/flatpak-builder-tools.git
fi

# Install required Python packages
pip install --user aiohttp toml packaging 2>/dev/null || true

# Install poetry export plugin if not already installed
echo "Verificando poetry-plugin-export..."
poetry self add poetry-plugin-export 2>/dev/null || true

# Generate requirements
echo "Exportando dependencias de Poetry..."
poetry export -f requirements.txt --without-hashes > requirements.txt

# Generate Flatpak sources
echo "Generando sources JSON para Flatpak..."
python3 flatpak-builder-tools/pip/flatpak-pip-generator \
    --runtime org.kde.Platform \
    --requirements-file requirements.txt \
    --output generated-sources

# Cleanup
rm requirements.txt

echo ""
echo "✓ Generado: generated-sources.json"
echo "Incluir este archivo en el manifest bajo python-deps sources"
