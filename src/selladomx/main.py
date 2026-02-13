"""Punto de entrada de la aplicación SelladoMX - QML UI"""
import sys
import os
import logging
from pathlib import Path

# Load environment variables BEFORE importing config (which reads env vars at module level)
from dotenv import load_dotenv
if not load_dotenv():
    load_dotenv(".env.development")

from PySide6.QtCore import QUrl, QEvent, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtQml import QQmlApplicationEngine

from .ui.qml_bridge.main_view_model import MainViewModel
from .ui.qml_bridge.signing_coordinator import SigningCoordinator
from .ui.qml_bridge.settings_bridge import SettingsBridge
from .utils.settings_manager import SettingsManager
from .utils.deep_link_handler import DeepLinkHandler
from .config import ONBOARDING_VERSION, COLOR_SUCCESS, COLOR_ERROR, BUY_CREDITS_URL, CREDIT_PRICE_DISPLAY

logger = logging.getLogger(__name__)

_SINGLE_INSTANCE_KEY = "selladomx-single-instance"


class SelladoMXApplication(QGuiApplication):
    """Custom QGuiApplication with single-instance and deep link support.

    Handles macOS FileOpen events for deep links when the app is already running,
    and implements a QLocalServer/QLocalSocket pattern to ensure only one instance
    runs at a time.
    """

    deepLinkReceived = Signal(str)

    def __init__(self, argv):
        super().__init__(argv)
        self._local_server = None

    def event(self, event):
        """Override to catch QEvent.FileOpen on macOS for deep links."""
        if event.type() == QEvent.FileOpen:
            url = event.url().toString()
            if url:
                logger.info("Received FileOpen event with URL")
                self.deepLinkReceived.emit(url)
                return True
        return super().event(event)

    def setup_single_instance(self) -> bool:
        """Set up single-instance enforcement.

        Returns:
            True if this is the first instance, False if another instance is running.
        """
        # Try to connect to an existing instance
        socket = QLocalSocket(self)
        socket.connectToServer(_SINGLE_INSTANCE_KEY)
        if socket.waitForConnected(500):
            # Another instance is running — send deep link if we have one
            if len(sys.argv) > 1 and sys.argv[1].startswith("selladomx://"):
                socket.write(sys.argv[1].encode("utf-8"))
                socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            logger.info("Another instance is running, forwarded deep link and exiting")
            return False

        # No existing instance — create the server
        self._local_server = QLocalServer(self)
        # Clean up stale socket file from previous crash
        QLocalServer.removeServer(_SINGLE_INSTANCE_KEY)
        if not self._local_server.listen(_SINGLE_INSTANCE_KEY):
            logger.warning(f"Failed to create local server: {self._local_server.errorString()}")
        else:
            self._local_server.newConnection.connect(self._on_new_connection)
            logger.info("Single-instance server started")
        return True

    def _on_new_connection(self):
        """Handle incoming connection from a second instance."""
        socket = self._local_server.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(1000)
            data = socket.readAll().data().decode("utf-8")
            socket.disconnectFromServer()
            if data:
                logger.info("Received deep link from second instance")
                self.deepLinkReceived.emit(data)


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

        # Notify QML for banner display
        view_model.tokenConfiguredViaDeepLink.emit()

        logger.info("Token configured successfully via deep link")

    except APIError as e:
        view_model._append_status_log(
            f"❌ Error al configurar token: {e.message}", COLOR_ERROR
        )
        logger.error(f"Failed to configure token via deep link: {e}")


def main():
    """Función principal de la aplicación"""
    setup_logging()
    logger.info("Starting SelladoMX with QML UI")

    # Set QML style to avoid native style warnings (must be before QGuiApplication)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    # Create SelladoMXApplication (custom subclass with deep link + single-instance)
    app = SelladoMXApplication(sys.argv)
    app.setApplicationName("SelladoMX")
    app.setOrganizationName("SelladoMX")
    app.setApplicationVersion("0.2.0")

    # Single-instance check: if another instance is running, forward deep link and exit
    if not app.setup_single_instance():
        sys.exit(0)

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

    # Expose app icon path for QML (works both in dev and packaged mode)
    if getattr(sys, "frozen", False):
        icon_file = Path(sys._MEIPASS) / "assets" / "selladomx.png"
    else:
        icon_file = Path(__file__).parent.parent.parent / "assets" / "selladomx.png"
    context.setContextProperty("appIconSource", QUrl.fromLocalFile(str(icon_file)))
    context.setContextProperty("buyCreditsUrl", BUY_CREDITS_URL)
    context.setContextProperty("creditPriceDisplay", CREDIT_PRICE_DISPLAY)

    # Connect deep link handler to view model method
    deep_link_handler.token_received.connect(
        lambda token: _handle_deep_link_token(token, settings_manager, view_model)
    )

    # Connect app-level deep link signal (FileOpen events + second instance messages)
    app.deepLinkReceived.connect(deep_link_handler.handle_url)

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
