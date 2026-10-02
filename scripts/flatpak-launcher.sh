#!/bin/bash
# Launcher script for Flatpak to set up Python environment correctly

export PYTHONPATH="/app/lib/python3.12/site-packages:$PYTHONPATH"

# Explicit Qt library and plugin paths: ldconfig is not available in the Flatpak sandbox
export LD_LIBRARY_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/lib:/app/lib:$LD_LIBRARY_PATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="/app/lib/python3.12/site-packages/PySide6/Qt/plugins"

exec python3 -m selladomx.main "$@"
