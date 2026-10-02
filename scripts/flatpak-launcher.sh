#!/bin/bash
# Launcher script for Flatpak to set up Python environment correctly

export PYTHONPATH="/app/lib/python3.12/site-packages:$PYTHONPATH"

export LD_LIBRARY_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/lib:/app/lib:$LD_LIBRARY_PATH"

# Disable ldconfig calls (not available in Flatpak sandbox)
export QT_QPA_PLATFORM_PLUGIN_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/plugins"

exec python3 -m selladomx.main "$@"
