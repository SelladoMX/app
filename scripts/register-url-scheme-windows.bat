@echo off
REM Register selladomx:// URL scheme for Windows
REM This script should be run as part of the Windows installer

echo Registering selladomx:// URL scheme...

reg add "HKEY_CURRENT_USER\Software\Classes\selladomx" /ve /d "URL:SelladoMX Protocol" /f
reg add "HKEY_CURRENT_USER\Software\Classes\selladomx" /v "URL Protocol" /d "" /f
reg add "HKEY_CURRENT_USER\Software\Classes\selladomx\shell\open\command" /ve /d "\"%~dp0SelladoMX.exe\" \"%%1\"" /f

echo.
echo URL scheme registered successfully!
echo You can now click selladomx:// links to open SelladoMX automatically.
echo.
pause
