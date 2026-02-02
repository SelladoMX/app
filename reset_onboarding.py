#!/usr/bin/env python3
"""Script para resetear el onboarding de SelladoMX."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from selladomx.utils.settings_manager import SettingsManager

def main():
    manager = SettingsManager()
    manager.reset_onboarding()
    print("✓ Onboarding reseteado")
    print("\nAhora ejecuta: poetry run selladomx")

    # Mostrar ubicación del archivo de configuración
    settings_file = manager.settings.fileName()
    print(f"\nArchivo de configuración: {settings_file}")
    print("(También puedes borrar este archivo manualmente)")

if __name__ == "__main__":
    main()
