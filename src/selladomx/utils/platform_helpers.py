"""Platform-specific helpers for URL scheme registration and other OS operations."""

import logging
import ntpath
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


# Must match AppId in installer/selladomx.iss.
WINDOWS_APP_ID = "{4285FAC5-53B6-436F-89B4-A58266D49505}"
WINDOWS_APP_MUTEX = "SelladoMXAppMutex"

_URL_KEY = r"Software\Classes\selladomx"
_COMMAND_KEY = rf"{_URL_KEY}\shell\open\command"
_UNINSTALL_KEY = (
    rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{WINDOWS_APP_ID}_is1"
)
_EXE_NAME = "selladomx.exe"

_app_mutex = None


def create_app_mutex():
    """Create the named mutex the installer checks to detect a running app.

    The handle is kept in a module global so it lives as long as the process;
    Windows releases it when the process exits.

    Returns:
        The mutex handle, or None when not on Windows or on failure
    """
    global _app_mutex
    if sys.platform != "win32" or _app_mutex:
        return _app_mutex

    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [
        wintypes.LPVOID,
        wintypes.BOOL,
        wintypes.LPCWSTR,
    ]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    handle = kernel32.CreateMutexW(None, False, WINDOWS_APP_MUTEX)
    if not handle:
        logger.warning(f"CreateMutexW failed: error {ctypes.get_last_error()}")
        return None
    _app_mutex = handle
    return handle


def _current_exe() -> str:
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])


def _windows_handler_command(exe_path: str) -> str:
    """Return the registry command that opens ``selladomx://`` links in exe_path."""
    return f'"{exe_path}" "%1"'


def _same_path(a: str, b: str) -> bool:
    return ntpath.normcase(ntpath.normpath(a)) == ntpath.normcase(ntpath.normpath(b))


def _exe_exists(path: str) -> bool:
    return os.path.isfile(path)


def _command_exe(command: str) -> str | None:
    """Extract the executable path from a ``shell\\open\\command`` value."""
    command = command.strip()
    if command.startswith('"'):
        end = command.find('"', 1)
        return command[1:end] if end > 1 else None
    return command.split(" ", 1)[0] or None


def should_update_url_handler(
    current_exe: str,
    registered_command: str | None,
    installed_exe: str | None,
) -> bool:
    """Decide whether this copy should write the ``selladomx://`` handler.

    The installed copy always takes the handler. A portable copy (an extracted
    zip, or a dev run) only takes it when nothing usable is registered, so it
    never steals links from a valid installed copy or another portable copy.

    Args:
        current_exe: Absolute path of the running executable
        registered_command: Current ``shell\\open\\command`` value, or None
        installed_exe: ``selladomx.exe`` under the installer's InstallLocation,
            or None when the app isn't installed

    Returns:
        True if the handler should be (re)written for current_exe
    """
    if registered_command is None:
        return True
    if registered_command.strip().lower() == (
        _windows_handler_command(current_exe).lower()
    ):
        return False
    if installed_exe and _same_path(current_exe, installed_exe):
        return True
    registered_exe = _command_exe(registered_command)
    return not registered_exe or not _exe_exists(registered_exe)


def _read_registered_command() -> str | None:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
            value, _ = winreg.QueryValueEx(key, "")
    except OSError:
        return None
    return value if isinstance(value, str) else None


def _installed_exe() -> str | None:
    """Return selladomx.exe in the installer's InstallLocation, if installed."""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _UNINSTALL_KEY) as key:
            location, _ = winreg.QueryValueEx(key, "InstallLocation")
    except OSError:
        return None
    if not isinstance(location, str) or not location:
        return None
    return ntpath.join(location, _EXE_NAME)


def register_url_scheme_windows():
    """Register selladomx:// URL scheme on Windows for this executable.

    Writes the same values as the installer's [Registry] section.

    Returns:
        bool: True if registration succeeded, False otherwise
    """
    if sys.platform != "win32":
        return False

    import winreg

    exe = _current_exe()
    try:
        # HKEY_CURRENT_USER doesn't require admin
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _URL_KEY) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "URL:SelladoMX Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, rf"{_URL_KEY}\DefaultIcon"
        ) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{exe},0")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _COMMAND_KEY) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, _windows_handler_command(exe))
    except OSError as e:
        logger.error(f"Failed to register URL scheme on Windows: {e}")
        return False

    logger.info("URL scheme registered for this executable")
    return True


def is_url_scheme_registered_windows():
    """Check if selladomx:// links on Windows open this copy of the app.

    Returns:
        bool: True if registered for this executable, False otherwise
    """
    if sys.platform != "win32":
        return False

    command = _read_registered_command()
    return command is not None and (
        command.strip().lower() == _windows_handler_command(_current_exe()).lower()
    )


def ensure_url_scheme_windows():
    """Write the selladomx:// handler if should_update_url_handler() says so.

    Returns:
        bool: True if the handler is usable (already set or written), False if
        writing it failed
    """
    if sys.platform != "win32":
        return False

    current = _current_exe()
    installed = _installed_exe()
    registered = _read_registered_command()
    if not should_update_url_handler(current, registered, installed):
        logger.info("URL handler left as is")
        return True
    return register_url_scheme_windows()


_DESKTOP_EXEC_RESERVED = set(" \t\n\"'\\><~|&;$*?#()`")


def quote_desktop_exec_arg(arg: str) -> str:
    """Quote one argument for the Exec key of a .desktop file.

    Follows the Desktop Entry spec: arguments with reserved characters are
    double-quoted with ``"`` ``\\`` ``$`` and backtick backslash-escaped; then
    the string-value escaping doubles every backslash, and ``%`` becomes ``%%``
    so it isn't read as a field code.

    Args:
        arg: Raw argument (e.g. the executable path)

    Returns:
        The argument as it must appear in the Exec value
    """
    if arg and not any(c in _DESKTOP_EXEC_RESERVED for c in arg):
        return arg.replace("%", "%%")
    quoted = "".join("\\" + c if c in '"`$\\' else c for c in arg)
    quoted = f'"{quoted}"'
    return quoted.replace("\\", "\\\\").replace("%", "%%")


def register_url_scheme_linux():
    """Register selladomx:// URL scheme on Linux.

    Returns:
        bool: True if registration succeeded, False otherwise
    """
    if sys.platform != "linux":
        return False

    # The Flatpak exports its own .desktop file with the URL handler; one
    # written from inside the sandbox would point at a path that only exists
    # inside it.
    if os.environ.get("FLATPAK_ID"):
        logger.info("Running inside Flatpak, URL scheme handled by the export")
        return True

    try:
        home = Path.home()

        # Check if running from AppImage
        appimage_path = os.environ.get("APPIMAGE")
        if not appimage_path:
            if getattr(sys, "frozen", False):
                appimage_path = sys.executable
            else:
                # Development mode
                appimage_path = "selladomx"

        desktop_file_content = f"""[Desktop Entry]
Type=Application
Name=SelladoMX
Comment=Firma digital de documentos PDF con e.firma
Exec={quote_desktop_exec_arg(appimage_path)} %u
Icon=selladomx
Terminal=false
Categories=Office;
MimeType=x-scheme-handler/selladomx;
StartupWMClass=selladomx
"""

        apps_dir = home / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = apps_dir / "selladomx.desktop"
        desktop_file.write_text(desktop_file_content)
        desktop_file.chmod(0o755)

        logger.info(f"Desktop file written to {desktop_file}")

        import subprocess

        try:
            result = subprocess.run(
                ["update-desktop-database", str(apps_dir)],
                capture_output=True,
                timeout=5,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Desktop database updated")
            else:
                logger.warning(f"update-desktop-database returned {result.returncode}")
        except FileNotFoundError:
            logger.warning("update-desktop-database not found, skipping")
        except Exception as e:
            logger.warning(f"Failed to update desktop database: {e}")

        try:
            result = subprocess.run(
                [
                    "xdg-mime",
                    "default",
                    "selladomx.desktop",
                    "x-scheme-handler/selladomx",
                ],
                capture_output=True,
                timeout=5,
                text=True,
            )

            if result.returncode == 0:
                logger.info("MIME type registered successfully")
            else:
                logger.warning(
                    f"xdg-mime returned {result.returncode}: {result.stderr}"
                )
        except FileNotFoundError:
            logger.warning("xdg-mime not found, skipping MIME registration")
        except Exception as e:
            logger.warning(f"Failed to register MIME type: {e}")

        logger.info("URL scheme registered on Linux")
        return True

    except Exception as e:
        logger.error(f"Failed to register URL scheme on Linux: {e}")
        return False


def is_url_scheme_registered_linux():
    """Check if URL scheme is already registered on Linux.

    Returns:
        bool: True if registered, False otherwise
    """
    if sys.platform != "linux":
        return False

    desktop_file = (
        Path.home() / ".local" / "share" / "applications" / "selladomx.desktop"
    )
    return desktop_file.exists()


def register_url_scheme():
    """Register URL scheme for the current platform.

    Returns:
        bool: True if registration succeeded or was already registered, False otherwise
    """
    if sys.platform == "win32":
        return ensure_url_scheme_windows()
    elif sys.platform == "linux":
        if is_url_scheme_registered_linux():
            logger.info("URL scheme already registered on Linux")
            return True
        return register_url_scheme_linux()
    elif sys.platform == "darwin":
        # macOS handles this via Info.plist in the .app bundle
        logger.info("URL scheme registration handled by macOS .app bundle")
        return True
    else:
        logger.warning(f"URL scheme registration not supported on {sys.platform}")
        return False


def is_url_scheme_registered():
    """Check if URL scheme is registered for the current platform.

    Returns:
        bool: True if registered, False otherwise
    """
    if sys.platform == "win32":
        return is_url_scheme_registered_windows()
    elif sys.platform == "linux":
        return is_url_scheme_registered_linux()
    elif sys.platform == "darwin":
        return True
    else:
        return False
