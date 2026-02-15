#!/bin/bash
# Launcher script for Flatpak to set up Python environment correctly

# Set Python path to include Flatpak-installed packages
export PYTHONPATH="/app/lib/python3.12/site-packages:$PYTHONPATH"

# Set library path for PySide6 Qt libraries
export LD_LIBRARY_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/lib:/app/lib:$LD_LIBRARY_PATH"

# Disable ldconfig calls (not available in Flatpak sandbox)
export QT_QPA_PLATFORM_PLUGIN_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/plugins"

# Run the actual application
exec python3 -m selladomx.main "$@"
