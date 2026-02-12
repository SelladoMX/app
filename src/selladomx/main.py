"""Punto de entrada de la aplicación SelladoMX"""
import sys
import logging
from pathlib import Path

# Load environment variables
# Priority: .env (local) → .env.development (default for dev) → hardcoded (production)
from dotenv import load_dotenv
if not load_dotenv():  # Try .env first
    load_dotenv(".env.development")  # Fallback to development defaults

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

from .ui.redesigned_main_view import RedesignedMainView
from .ui.onboarding.onboarding_dialog import OnboardingDialog
from .utils.settings_manager import SettingsManager
from .utils.deep_link_handler import DeepLinkHandler
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
    """Configure light theme palette"""
    palette = QPalette()

    # Base colors (light background with dark text)
    palette.setColor(QPalette.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.WindowText, QColor("#1D1D1F"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.AlternateBase, QColor("#F5F5F7"))
    palette.setColor(QPalette.Text, QColor("#1D1D1F"))
    palette.setColor(QPalette.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ButtonText, QColor("#1D1D1F"))

    # Highlight colors (teal selection)
    palette.setColor(QPalette.Highlight, QColor("#0D9488"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    # Link colors (teal)
    palette.setColor(QPalette.Link, QColor("#0D9488"))
    palette.setColor(QPalette.LinkVisited, QColor("#0F766E"))

    # Disabled state
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#C7C7CC"))
    palette.setColor(QPalette.Disabled, QPalette.Base, QColor("#F5F5F7"))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#E5E5E7"))

    # Tooltips
    palette.setColor(QPalette.ToolTipBase, QColor("#1D1D1F"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))

    app.setPalette(palette)


def _handle_deep_link_token(token: str, settings_manager: SettingsManager, window):
    """Handle token received via deep link.

    Args:
        token: Token string from magic link
        settings_manager: Settings manager instance
        window: Main window instance
    """
    from PySide6.QtWidgets import QMessageBox
    from .api.client import SelladoMXAPIClient
    from .api.exceptions import APIError

    logger = logging.getLogger(__name__)

    # Test token with API
    try:
        client = SelladoMXAPIClient(api_key=token)
        balance_response = client.get_balance()

        # Save token and metadata
        settings_manager.set_token(token)
        settings_manager.set_token_info(balance_response["token_info"])
        settings_manager.set_last_credit_balance(balance_response["credits_remaining"])

        # Refresh UI
        window._update_credit_label()
        window._update_tsa_credits_label()
        window.chk_professional_tsa.setEnabled(True)

        # Show success message
        QMessageBox.information(
            window,
            "Token configurado",
            f"✅ Token configurado exitosamente\n\n"
            f"Créditos disponibles: {balance_response['credits_remaining']}\n"
            f"Email: {balance_response['email']}"
        )

        logger.info("Token configured successfully via deep link")

    except APIError as e:
        QMessageBox.critical(
            window,
            "Error al configurar token",
            f"No se pudo validar el token:\n{e.message}"
        )
        logger.error(f"Failed to configure token via deep link: {e}")


def main():
    """Función principal de la aplicación"""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting SelladoMX application")

    app = QApplication(sys.argv)
    app.setApplicationName("SelladoMX")
    app.setOrganizationName("SelladoMX")
    app.setApplicationVersion("0.1.0")

    # Setup light theme
    app.setStyle("Fusion")
    setup_light_palette(app)
    logger.info("Light theme palette configured")

    # Load light theme stylesheet
    qss_path = Path(__file__).parent / "ui" / "styles" / "theme_light.qss"
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Theme loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load theme: {e}")

    # Initialize settings manager
    settings_manager = SettingsManager()

    # Register URL scheme on first launch (silent registration)
    if not settings_manager.has_attempted_url_scheme_registration():
        logger.info("First launch detected, registering URL scheme...")
        from .utils.platform_helpers import register_url_scheme
        success = register_url_scheme()
        if success:
            logger.info("URL scheme registered successfully")
        else:
            logger.warning("URL scheme registration failed (non-critical)")
        # Mark as attempted regardless of success (don't spam logs on every launch)
        settings_manager.mark_url_scheme_registration_attempted()

    # Create deep link handler BEFORE showing any windows
    deep_link_handler = DeepLinkHandler()
    deep_link_url = None

    # Check for deep link in command line arguments
    if len(sys.argv) > 1 and sys.argv[1].startswith("selladomx://"):
        deep_link_url = sys.argv[1]
        logger.info(f"Received deep link on startup: {deep_link_url}")

    # Check if onboarding is needed
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

    # Connect deep link handler to window method
    deep_link_handler.token_received.connect(
        lambda token: _handle_deep_link_token(token, settings_manager, window)
    )

    # Process deep link if provided on startup
    if deep_link_url:
        deep_link_handler.handle_url(deep_link_url)

    window.show()

    logger.info("Application started successfully")
    exit_code = app.exec()

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
