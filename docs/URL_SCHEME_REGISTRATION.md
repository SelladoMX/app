# URL Scheme Registration (Magic Links)

SelladoMX supports automatic token configuration via magic links using the `selladomx://` URL scheme.

## How It Works

When you receive a token via email, you can click a magic link like:
```
selladomx://auth?token=smx_xxxxxxxxxxxxx
```

This will:
1. Open the SelladoMX application automatically
2. Validate the token with the backend
3. Configure your authentication automatically
4. Display your credit balance and account info

## Automatic Registration

Starting from version 0.1.0, SelladoMX **automatically registers** the URL scheme on first launch.

### Windows
- Registers in `HKEY_CURRENT_USER\Software\Classes\selladomx`
- No administrator rights required
- Works with portable .exe files

### Linux
- Flatpak automatically registers the URL scheme via desktop file
- Desktop entry at `/var/lib/flatpak/exports/share/applications/` (system) or `~/.local/share/flatpak/exports/share/applications/` (user)
- MIME type handler registered automatically by Flatpak

### macOS
- Registration handled by the .app bundle's `Info.plist`
- Configured during build via PyInstaller

## Testing

Test if the URL scheme is registered:

```bash
# Run the test script
python scripts/test_url_scheme.py
```

Or manually test:

### Windows
```cmd
# Open from Command Prompt
start selladomx://auth?token=smx_test123
```

### Linux
```bash
# Open from terminal
xdg-open "selladomx://auth?token=smx_test123"
```

### macOS
```bash
# Open from terminal
open "selladomx://auth?token=smx_test123"
```

## Manual Registration (Fallback)

If automatic registration fails, you can register manually:

### Windows
Run the batch script:
```cmd
scripts\register-url-scheme-windows.bat
```

Or import the registry manually by creating a `.reg` file with:
```registry
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\selladomx]
@="URL:SelladoMX Protocol"
"URL Protocol"=""

[HKEY_CURRENT_USER\Software\Classes\selladomx\shell\open\command]
@="\"C:\\Path\\To\\SelladoMX.exe\" \"%1\""
```

### Linux
Copy the desktop file:
```bash
# Copy from assets
cp assets/selladomx.desktop ~/.local/share/applications/

# Make executable
chmod +x ~/.local/share/applications/selladomx.desktop

# Register MIME type
xdg-mime default selladomx.desktop x-scheme-handler/selladomx

# Update database
update-desktop-database ~/.local/share/applications/
```

## Troubleshooting

### Windows: "Protocol not recognized"
1. Check registry key exists:
   ```cmd
   reg query "HKEY_CURRENT_USER\Software\Classes\selladomx"
   ```
2. Verify executable path in registry is correct
3. Re-run `register-url-scheme-windows.bat`

### Linux: Links don't open the app
1. Check desktop file exists:
   ```bash
   ls ~/.local/share/applications/selladomx.desktop
   ```
2. Verify MIME type association:
   ```bash
   xdg-mime query default x-scheme-handler/selladomx
   ```
   Should return: `selladomx.desktop`
3. Check desktop file has correct Exec path
4. Re-run registration:
   ```bash
   python scripts/test_url_scheme.py
   ```

### macOS: Links don't work
1. Ensure you're running from the .app bundle (not the raw executable)
2. Check Info.plist contains `CFBundleURLTypes`
3. Rebuild the .app:
   ```bash
   ./scripts/build.sh
   ```

## Security Considerations

- The URL scheme handler validates token format before processing
- Only `selladomx://auth?token=XXX` URLs are accepted
- Token must match the `smx_[0-9a-f]{5,}` pattern
- Invalid URLs are logged and rejected silently
- Backend validates all tokens before accepting them

## Implementation Details

The URL scheme registration is handled by:

1. **Platform Helpers** (`src/selladomx/utils/platform_helpers.py`)
   - Cross-platform registration functions
   - Detection of existing registrations
   - Error handling and logging

2. **Main Application** (`src/selladomx/main.py`)
   - Checks registration status on startup
   - Registers silently on first launch
   - Processes deep link arguments

3. **Deep Link Handler** (`src/selladomx/utils/deep_link_handler.py`)
   - Parses and validates URLs
   - Extracts tokens securely
   - Emits signals to UI

4. **Settings Manager** (`src/selladomx/utils/settings_manager.py`)
   - Tracks registration status
   - Prevents duplicate registrations
   - Stores configuration

## For Developers

To test during development:

```bash
# Install in development mode
pip install -e .

# Run with deep link argument
python -m selladomx "selladomx://auth?token=smx_test123"
```

The app will automatically register the URL scheme on first run, even in development mode.
