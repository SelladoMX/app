"""Punto de entrada de la aplicación SelladoMX - QML UI"""
import sys
import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .ui.qml_bridge.main_view_model import MainViewModel
from .ui.qml_bridge.signing_coordinator import SigningCoordinator
from .ui.qml_bridge.settings_bridge import SettingsBridge
from .utils.settings_manager import SettingsManager
from .utils.deep_link_handler import DeepLinkHandler
from .config import ONBOARDING_VERSION, COLOR_SUCCESS, COLOR_ERROR

logger = logging.getLogger(__name__)


def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _handle_deep_link_token(
    token: str, settings_manager: SettingsManager, view_model: MainViewModel
):
    """Handle token received via deep link.

    Args:
        token: Token string from magic link
        settings_manager: Settings manager instance
        view_model: Main view model instance
    """
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

        # Refresh view model
        view_model._refresh_credit_balance()

        # Show success message via status log
        view_model._append_status_log(
            f"✅ Token configurado exitosamente - {balance_response['credits_remaining']} créditos disponibles",
            COLOR_SUCCESS,
        )

        logger.info("Token configured successfully via deep link")

    except APIError as e:
        view_model._append_status_log(
            f"❌ Error al configurar token: {e.message}", COLOR_ERROR
        )
        logger.error(f"Failed to configure token via deep link: {e}")


def main():
    """Función principal de la aplicación"""
    # Load environment variables
    if not load_dotenv():
        load_dotenv(".env.development")

    setup_logging()
    logger.info("Starting SelladoMX with QML UI")

    # Set QML style to avoid native style warnings (must be before QGuiApplication)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    # Create QGuiApplication (for QML, not QApplication)
    app = QGuiApplication(sys.argv)
    app.setApplicationName("SelladoMX")
    app.setOrganizationName("SelladoMX")
    app.setApplicationVersion("0.2.0")

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
        settings_manager.mark_url_scheme_registration_attempted()

    # Create deep link handler BEFORE creating engine
    deep_link_handler = DeepLinkHandler()
    deep_link_url = None

    # Check for deep link in command line arguments
    if len(sys.argv) > 1 and sys.argv[1].startswith("selladomx://"):
        deep_link_url = sys.argv[1]
        logger.info(f"Received deep link on startup: {deep_link_url}")

    # Initialize backend components
    coordinator = SigningCoordinator()
    view_model = MainViewModel(settings_manager, coordinator)
    settings_bridge = SettingsBridge(settings_manager)

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Expose ViewModels to QML as context properties
    context = engine.rootContext()
    context.setContextProperty("mainViewModel", view_model)
    context.setContextProperty("settingsBridge", settings_bridge)

    # Expose app icon path for QML
    icon_file = Path(__file__).parent.parent.parent / "assets" / "icon.png"
    context.setContextProperty("appIconSource", QUrl.fromLocalFile(str(icon_file)))

    # Connect deep link handler to view model method
    deep_link_handler.token_received.connect(
        lambda token: _handle_deep_link_token(token, settings_manager, view_model)
    )

    # Load main QML file
    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"

    if not qml_file.exists():
        logger.error(f"QML file not found: {qml_file}")
        sys.exit(-1)

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # Check if QML loaded successfully
    if not engine.rootObjects():
        logger.error("Failed to load QML - no root objects created")
        sys.exit(-1)

    logger.info("QML UI loaded successfully")

    # Process deep link if provided on startup
    if deep_link_url:
        deep_link_handler.handle_url(deep_link_url)

    # Show onboarding if needed (AFTER main window is loaded)
    if not settings_manager.has_completed_onboarding():
        logger.info("First run detected, showing onboarding")

        # Get the root window
        root_objects = engine.rootObjects()
        if root_objects:
            root_window = root_objects[0]

            # Call the showOnboarding method on the main QML window
            from PySide6.QtCore import QMetaObject, Qt

            QMetaObject.invokeMethod(root_window, "showOnboarding", Qt.QueuedConnection)
        else:
            logger.warning("No root objects found, skipping onboarding")
            settings_manager.mark_onboarding_completed()
            settings_manager.set_onboarding_version(ONBOARDING_VERSION)

    logger.info("Application started successfully with QML UI")
    exit_code = app.exec()

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
