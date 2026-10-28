#!/bin/bash
# Launcher script for Flatpak to set up Python environment correctly

# The runtime decides the Python version; pip installs under /app/lib/python3.X
SITE_PACKAGES="/app/lib/$(python3 -c 'import sys; print(f"python{sys.version_info[0]}.{sys.version_info[1]}")')/site-packages"

export PYTHONPATH="$SITE_PACKAGES:$PYTHONPATH"

# Explicit Qt library and plugin paths: ldconfig is not available in the Flatpak sandbox
export LD_LIBRARY_PATH="$SITE_PACKAGES/PySide6/Qt/lib:/app/lib:$LD_LIBRARY_PATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$SITE_PACKAGES/PySide6/Qt/plugins"

exec python3 -m selladomx.main "$@"
