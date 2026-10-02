================================================================================
  SelladoMX - Portable Version for Windows
================================================================================

HOW TO RUN:
-----------
1. Extract this ZIP file to any folder on your computer
2. Double-click "selladomx.exe" to launch the application

PORTABLE MODE:
--------------
- No installation required
- No admin rights needed
- Copy this entire folder to a USB drive to run from anywhere
- Settings are saved in the Windows registry of the current user, not in
  this folder. On first launch the app also registers the selladomx:// link
  handler there (current user only)

FIRST RUN SECURITY WARNING:
---------------------------
When you first run selladomx.exe, Windows may show a security warning:
  "Windows protected your PC" or "Unknown publisher"

This happens because the application is not code-signed.

To proceed:
1. Click "More info" on the security warning
2. Click "Run anyway" button
3. The app will launch normally
4. You may need to do this only once

WHAT IS SELLADOMX?
------------------
SelladoMX is a PDF signing application designed for Mexican digital
signature requirements. It allows you to digitally sign PDF documents
using your electronic signature certificate (e.firma).

SYSTEM REQUIREMENTS:
--------------------
- Windows 10 or later
- 200 MB of free disk space
- Your e.firma certificate files (.cer and .key)

NEED HELP?
----------
- Report issues: https://github.com/SelladoMX/app/issues
- Open source: Licensed under MIT
- Documentation: See README.md in the GitHub repository

TECHNICAL DETAILS:
------------------
- Built with Python and PySide6 (Qt6)
- Uses pyhanko for PDF signing
- Supports Mexican e.firma certificates
- No telemetry; PDFs never leave your computer

================================================================================
License: MIT License
Website: https://github.com/SelladoMX/app
================================================================================
