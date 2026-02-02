"""Test script for onboarding dialog."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from selladomx.ui.onboarding.onboarding_dialog import OnboardingDialog
from selladomx.utils.settings_manager import SettingsManager

def main():
    app = QApplication(sys.argv)

    # Load theme
    qss_path = Path(__file__).parent / "src" / "selladomx" / "ui" / "styles" / "main_theme.qss"
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Could not load theme: {e}")

    # Reset onboarding for testing
    settings = SettingsManager()
    settings.reset_onboarding()

    # Show onboarding
    dialog = OnboardingDialog()
    result = dialog.exec()

    print(f"Dialog result: {'Accepted' if result else 'Rejected'}")

    if result:
        settings.mark_onboarding_completed()
        print("Onboarding marked as completed")

    sys.exit(0)

if __name__ == "__main__":
    main()
