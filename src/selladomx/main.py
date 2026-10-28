"""Punto de entrada de la aplicación SelladoMX - QML UI"""

import getpass
import hashlib
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# config.py reads env vars at import time, so .env must be loaded before
# anything that imports it. Frozen builds skip .env entirely: a stray .env in
# the working directory could otherwise redirect the API, and the user's token.
if not getattr(sys, "frozen", False):
    _PROJECT_ROOT = Path(__file__).resolve().parents[2]
    if not load_dotenv(_PROJECT_ROOT / ".env"):
        load_dotenv(_PROJECT_ROOT / ".env.development")

from PySide6.QtCore import QUrl, QEvent, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from . import __version__
from .utils.deep_link_handler import describe_deep_link
from .utils.logging_setup import (
    install_excepthook,
    install_qt_message_handler,
    log_startup_info,
    setup_logging,
)
from .utils.platform_helpers import create_app_mutex

logger = logging.getLogger(__name__)


def single_instance_server_name() -> str:
    """Return the per-user name of the single-instance local server.

    On macOS and Linux the name becomes a socket file in a shared temp
    directory, so it must differ between users of the same machine.

    Returns:
        ``selladomx-single-instance-<hash of the user name>``
    """
    try:
        user = getpass.getuser()
    except Exception:
        user = str(Path.home())
    digest = hashlib.sha256(user.encode("utf-8")).hexdigest()[:16]
    return f"selladomx-single-instance-{digest}"


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
        server_name = single_instance_server_name()
        socket = QLocalSocket(self)
        socket.connectToServer(server_name)
        if socket.waitForConnected(500):
            if len(sys.argv) > 1 and sys.argv[1].startswith("selladomx://"):
                socket.write(sys.argv[1].encode("utf-8"))
                socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            logger.info("Another instance is running, forwarded deep link and exiting")
            return False

        self._local_server = QLocalServer(self)
        self._local_server.setSocketOptions(QLocalServer.UserAccessOption)
        # Clean up stale socket file from previous crash
        QLocalServer.removeServer(server_name)
        if not self._local_server.listen(server_name):
            logger.warning(
                f"Failed to create local server: {self._local_server.errorString()}"
            )
        else:
            self._local_server.newConnection.connect(self._on_new_connection)
            logger.info("Single-instance server started")
        return True

    def _on_new_connection(self):
        """Handle incoming connection from a second instance."""
        socket = self._local_server.nextPendingConnection()
        if socket:
            socket.waitForReadyRead(1000)
            data = socket.readAll().data().decode("utf-8", errors="replace")
            socket.disconnectFromServer()
            if data:
                logger.info("Received deep link from second instance")
                self.deepLinkReceived.emit(data)


def main():
    """Función principal de la aplicación"""
    log_file = setup_logging()
    install_excepthook()
    install_qt_message_handler()
    log_startup_info(__version__, log_file)
    create_app_mutex()

    # Imported after setup_logging() so config's import-time log lines are kept
    from .ui.qml_bridge.main_view_model import MainViewModel
    from .ui.qml_bridge.signing_coordinator import SigningCoordinator
    from .ui.qml_bridge.settings_bridge import SettingsBridge
    from .utils.settings_manager import SettingsManager
    from .utils.deep_link_handler import DeepLinkHandler
    from .utils.update_checker import UpdateChecker
    from .config import (
        ONBOARDING_VERSION,
        BUY_CREDITS_URL,
        CREDIT_PRICE_DISPLAY,
    )
    from PySide6.QtQml import QQmlApplicationEngine

    # Set QML style to avoid native style warnings (must be before QGuiApplication)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    app = SelladoMXApplication(sys.argv)
    app.setApplicationName("SelladoMX")
    app.setOrganizationName("SelladoMX")
    app.setApplicationVersion(__version__)

    if not app.setup_single_instance():
        sys.exit(0)

    settings_manager = SettingsManager()

    # On Windows the handler stores an exe path, so it is checked on every
    # launch; see should_update_url_handler() for which copy gets the links.
    if (
        sys.platform == "win32"
        or not settings_manager.has_attempted_url_scheme_registration()
    ):
        logger.info("Checking URL scheme registration...")
        from .utils.platform_helpers import register_url_scheme

        # Link registration is optional; nothing in it may stop the app starting
        try:
            success = register_url_scheme()
        except Exception:
            logger.exception("URL scheme registration crashed")
            success = False
        if success:
            logger.info("URL scheme registered successfully")
        else:
            logger.warning("URL scheme registration failed (non-critical)")
        settings_manager.mark_url_scheme_registration_attempted()

    # Create deep link handler BEFORE creating engine
    deep_link_handler = DeepLinkHandler()
    deep_link_url = None

    if len(sys.argv) > 1 and sys.argv[1].startswith("selladomx://"):
        deep_link_url = sys.argv[1]
        logger.info(
            f"Received deep link on startup: {describe_deep_link(deep_link_url)}"
        )

    coordinator = SigningCoordinator()
    view_model = MainViewModel(settings_manager, coordinator)
    settings_bridge = SettingsBridge(settings_manager)

    engine = QQmlApplicationEngine()

    context = engine.rootContext()
    context.setContextProperty("mainViewModel", view_model)
    context.setContextProperty("settingsBridge", settings_bridge)

    # Bundled assets live under sys._MEIPASS in PyInstaller builds
    if getattr(sys, "frozen", False):
        icon_file = Path(sys._MEIPASS) / "assets" / "selladomx.png"
    else:
        icon_file = Path(__file__).parent.parent.parent / "assets" / "selladomx.png"
    context.setContextProperty("appIconSource", QUrl.fromLocalFile(str(icon_file)))
    context.setContextProperty("appVersion", __version__)
    context.setContextProperty("buyCreditsUrl", BUY_CREDITS_URL)
    context.setContextProperty("creditPriceDisplay", CREDIT_PRICE_DISPLAY)

    update_checker = UpdateChecker(__version__)
    context.setContextProperty("updateChecker", update_checker)

    deep_link_handler.token_received.connect(view_model.handleDeepLinkToken)

    # Connect app-level deep link signal (FileOpen events + second instance messages)
    app.deepLinkReceived.connect(deep_link_handler.handle_url)

    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"

    if not qml_file.exists():
        logger.error(f"QML file not found: {qml_file}")
        sys.exit(-1)

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        logger.error("Failed to load QML - no root objects created")
        sys.exit(-1)

    logger.info("QML UI loaded successfully")

    if deep_link_url:
        deep_link_handler.handle_url(deep_link_url)

    # Must run after the root window has loaded
    if not settings_manager.has_completed_onboarding():
        logger.info("First run detected, showing onboarding")

        root_objects = engine.rootObjects()
        if root_objects:
            root_window = root_objects[0]

            from PySide6.QtCore import QMetaObject, Qt

            QMetaObject.invokeMethod(root_window, "showOnboarding", Qt.QueuedConnection)
        else:
            logger.warning("No root objects found, skipping onboarding")
            settings_manager.mark_onboarding_completed()
            settings_manager.set_onboarding_version(ONBOARDING_VERSION)

    logger.info("Application started successfully with QML UI")
    exit_code = app.exec()

    # Destroy the QML engine while the context-property objects still exist;
    # otherwise bindings re-evaluate against null view models during teardown
    # and flood the log with TypeErrors.
    del engine

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
