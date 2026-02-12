"""Platform-specific helpers for URL scheme registration and other OS operations."""
import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def register_url_scheme_windows():
    """Register selladomx:// URL scheme on Windows.

    Returns:
        bool: True if registration succeeded, False otherwise
    """
    if sys.platform != "win32":
        return False

    try:
        import winreg

        # Get executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            exe_path = sys.executable
        else:
            # Running as script (development)
            exe_path = sys.argv[0]

        exe_path = os.path.abspath(exe_path)

        # Register URL scheme in HKEY_CURRENT_USER (doesn't require admin)
        key_path = r"Software\Classes\selladomx"

        # Create main key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "URL:SelladoMX Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

        # Create shell\open\command key
        command_path = rf"{key_path}\shell\open\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')

        logger.info(f"URL scheme registered for {exe_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to register URL scheme on Windows: {e}")
        return False


def is_url_scheme_registered_windows():
    """Check if URL scheme is already registered on Windows.

    Returns:
        bool: True if registered, False otherwise
    """
    if sys.platform != "win32":
        return False

    try:
        import winreg
        key_path = r"Software\Classes\selladomx\shell\open\command"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValue(key, "")
            return bool(value)
    except:
        return False


def register_url_scheme_linux():
    """Register selladomx:// URL scheme on Linux.

    Returns:
        bool: True if registration succeeded, False otherwise
    """
    if sys.platform != "linux":
        return False

    try:
        home = Path.home()

        # Check if running from AppImage
        appimage_path = os.environ.get("APPIMAGE")
        if not appimage_path:
            # Not running from AppImage, check if frozen
            if getattr(sys, 'frozen', False):
                appimage_path = sys.executable
            else:
                # Development mode
                appimage_path = "selladomx"

        # Create desktop entry
        desktop_file_content = f"""[Desktop Entry]
Type=Application
Name=SelladoMX
Comment=Firma digital de documentos PDF con e.firma
Exec={appimage_path} %u
Icon=selladomx
Terminal=false
Categories=Office;
MimeType=x-scheme-handler/selladomx;
StartupWMClass=selladomx
"""

        # Write to ~/.local/share/applications/
        apps_dir = home / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = apps_dir / "selladomx.desktop"
        desktop_file.write_text(desktop_file_content)
        desktop_file.chmod(0o755)

        logger.info(f"Desktop file written to {desktop_file}")

        # Update desktop database
        import subprocess
        try:
            result = subprocess.run(
                ["update-desktop-database", str(apps_dir)],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                logger.info("Desktop database updated")
            else:
                logger.warning(f"update-desktop-database returned {result.returncode}")
        except FileNotFoundError:
            logger.warning("update-desktop-database not found, skipping")
        except Exception as e:
            logger.warning(f"Failed to update desktop database: {e}")

        # Register MIME type
        try:
            result = subprocess.run([
                "xdg-mime", "default", "selladomx.desktop",
                "x-scheme-handler/selladomx"
            ], capture_output=True, timeout=5, text=True)

            if result.returncode == 0:
                logger.info("MIME type registered successfully")
            else:
                logger.warning(f"xdg-mime returned {result.returncode}: {result.stderr}")
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

    desktop_file = Path.home() / ".local" / "share" / "applications" / "selladomx.desktop"
    return desktop_file.exists()


def register_url_scheme():
    """Register URL scheme for the current platform.

    Returns:
        bool: True if registration succeeded or was already registered, False otherwise
    """
    if sys.platform == "win32":
        if is_url_scheme_registered_windows():
            logger.info("URL scheme already registered on Windows")
            return True
        return register_url_scheme_windows()
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
        # macOS handles this via Info.plist
        return True
    else:
        return False
