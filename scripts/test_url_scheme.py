#!/usr/bin/env python3
"""Test URL scheme registration for SelladoMX.

This script tests if the selladomx:// URL scheme is properly registered
and provides diagnostic information.
"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from selladomx.utils.platform_helpers import (
    is_url_scheme_registered,
    register_url_scheme,
    is_url_scheme_registered_windows,
    is_url_scheme_registered_linux,
)


def main():
    print("=" * 60)
    print("SelladoMX URL Scheme Registration Test")
    print("=" * 60)
    print()

    # Detect platform
    print(f"Platform: {sys.platform}")
    print()

    # Check registration status
    print("Checking current registration status...")
    is_registered = is_url_scheme_registered()

    if is_registered:
        print("✅ URL scheme is REGISTERED")
        print()
        print("The selladomx:// protocol should work.")
        print("Try opening: selladomx://auth?token=smx_test123")
    else:
        print("❌ URL scheme is NOT registered")
        print()

        # Ask if user wants to register
        response = input("Would you like to register it now? (y/n): ").strip().lower()

        if response == 'y':
            print()
            print("Attempting registration...")
            success = register_url_scheme()

            if success:
                print("✅ Registration successful!")
                print()
                print("You can now use selladomx:// links.")
                print("Try: selladomx://auth?token=smx_test123")
            else:
                print("❌ Registration failed.")
                print()
                print("Please check the logs for more details.")
                return 1
        else:
            print()
            print("Registration skipped.")
            return 0

    print()
    print("=" * 60)
    print("Platform-specific details:")
    print("=" * 60)

    if sys.platform == "win32":
        print()
        print("Windows Registry Check:")
        if is_url_scheme_registered_windows():
            print("✅ Registry key exists at:")
            print("   HKEY_CURRENT_USER\\Software\\Classes\\selladomx")
        else:
            print("❌ Registry key not found")

    elif sys.platform == "linux":
        print()
        print("Linux Desktop Entry Check:")
        desktop_file = Path.home() / ".local" / "share" / "applications" / "selladomx.desktop"
        if desktop_file.exists():
            print(f"✅ Desktop file exists at:")
            print(f"   {desktop_file}")
            print()
            print("Contents:")
            print(desktop_file.read_text())
        else:
            print(f"❌ Desktop file not found at:")
            print(f"   {desktop_file}")

    elif sys.platform == "darwin":
        print()
        print("macOS Note:")
        print("URL scheme registration is handled automatically by the .app bundle.")
        print("Check Info.plist for CFBundleURLTypes configuration.")

    print()
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print("Aborted by user.")
        sys.exit(130)
