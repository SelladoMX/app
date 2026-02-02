"""Test script for redesigned main view."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from selladomx.ui.redesigned_main_view import RedesignedMainView

def main():
    app = QApplication(sys.argv)

    # Load theme
    qss_path = Path(__file__).parent / "src" / "selladomx" / "ui" / "styles" / "main_theme.qss"
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        print("Theme loaded successfully")
    except Exception as e:
        print(f"Could not load theme: {e}")

    # Show redesigned main view
    window = RedesignedMainView()
    window.show()

    print("Window shown, starting event loop")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
