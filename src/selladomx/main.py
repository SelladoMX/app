"""Punto de entrada de la aplicación SelladoMX"""
import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

from .ui.redesigned_main_view import RedesignedMainView
from .ui.onboarding.onboarding_dialog import OnboardingDialog
from .utils.settings_manager import SettingsManager
from .config import ONBOARDING_VERSION


def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def setup_light_palette(app: QApplication):
    """Fuerza una paleta de colores clara para ignorar el modo oscuro del sistema"""
    palette = QPalette()

    # Colores base (fondo y primer plano)
    palette.setColor(QPalette.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.WindowText, QColor("#1D1D1F"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase, QColor("#F5F5F7"))
    palette.setColor(QPalette.Text, QColor("#1D1D1F"))
    palette.setColor(QPalette.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ButtonText, QColor("#1D1D1F"))

    # Colores de resaltado (selección)
    palette.setColor(QPalette.Highlight, QColor("#007AFF"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    # Colores de enlaces
    palette.setColor(QPalette.Link, QColor("#007AFF"))
    palette.setColor(QPalette.LinkVisited, QColor("#5856D6"))

    # Colores para widgets deshabilitados
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor("#F5F5F7"))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#E5E5E7"))

    # Tooltips
    palette.setColor(QPalette.ToolTipBase, QColor("#1D1D1F"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))

    app.setPalette(palette)


def main():
    """Función principal de la aplicación"""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting SelladoMX application")

    app = QApplication(sys.argv)
    app.setApplicationName("SelladoMX")
    app.setOrganizationName("SelladoMX")
    app.setApplicationVersion("0.1.0")

    # Force light mode (ignore system dark mode)
    app.setStyle("Fusion")
    setup_light_palette(app)
    logger.info("Forced light mode with custom palette")

    # Load global theme
    qss_path = Path(__file__).parent / "ui" / "styles" / "main_theme.qss"
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Theme loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load theme: {e}")

    # Check if onboarding is needed
    settings_manager = SettingsManager()
    if not settings_manager.has_completed_onboarding():
        logger.info("First run detected, showing onboarding")
        onboarding = OnboardingDialog()
        result = onboarding.exec()

        if result == QDialog.Accepted:
            settings_manager.mark_onboarding_completed()
            settings_manager.set_onboarding_version(ONBOARDING_VERSION)
            logger.info("Onboarding completed")
        else:
            logger.info("Onboarding cancelled, exiting")
            sys.exit(0)

    # Show main window
    window = RedesignedMainView()
    window.show()

    logger.info("Application started successfully")
    exit_code = app.exec()

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
