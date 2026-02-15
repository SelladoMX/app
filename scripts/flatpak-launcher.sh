#!/bin/bash
# Launcher script for Flatpak to set up Python environment correctly

# Set Python path to include Flatpak-installed packages
export PYTHONPATH="/app/lib/python3.12/site-packages:$PYTHONPATH"

# Run the actual application
exec python3 -m selladomx.main "$@"
