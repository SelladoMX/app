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
4. Show your remaining credits

## Automatic Registration

SelladoMX attempts registration once, on first launch; the attempt is recorded in QSettings (`system/url_scheme_registered`) whether or not it succeeded.

### Windows
- Registers in `HKEY_CURRENT_USER\Software\Classes\selladomx`
- No administrator rights required
- Stores the path of the running `selladomx.exe`; if the folder is moved, the registered path is stale and must be re-registered

### Linux
- The Flatpak exports `com.selladomx.SelladoMX.desktop` (with `MimeType=x-scheme-handler/selladomx`) to `/var/lib/flatpak/exports/share/applications/` (system install) or `~/.local/share/flatpak/exports/share/applications/` (user install)
- On first launch the app also writes `~/.local/share/applications/selladomx.desktop` and runs `xdg-mime default selladomx.desktop x-scheme-handler/selladomx`

### macOS
- Registration handled by `CFBundleURLTypes` in the .app bundle's `Info.plist`, set in `selladomx.spec`

## Testing

Check registration (offers to register if missing):

```bash
poetry run python scripts/test_url_scheme.py
```

Open a test link:

```bash
start selladomx://auth?token=smx_test123          # Windows (cmd)
xdg-open "selladomx://auth?token=smx_test123"     # Linux
open "selladomx://auth?token=smx_test123"         # macOS
```

## Manual Registration (Fallback)

If automatic registration fails, you can register manually:

### Windows
Copy `scripts\register-url-scheme-windows.bat` next to `selladomx.exe` (it registers the exe in its own folder) and run it.

Or import the registry manually by creating a `.reg` file with:
```registry
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\selladomx]
@="URL:SelladoMX Protocol"
"URL Protocol"=""

[HKEY_CURRENT_USER\Software\Classes\selladomx\shell\open\command]
@="\"C:\\Path\\To\\selladomx.exe\" \"%1\""
```

### Linux (without Flatpak)
```bash
cp assets/selladomx.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/selladomx.desktop
xdg-mime default selladomx.desktop x-scheme-handler/selladomx
update-desktop-database ~/.local/share/applications/
```

`assets/selladomx.desktop` runs `selladomx %u`, so `selladomx` must be on `PATH`.

## Troubleshooting

### Windows: "Protocol not recognized"
1. Check registry key exists:
   ```cmd
   reg query "HKEY_CURRENT_USER\Software\Classes\selladomx"
   ```
2. Verify executable path in registry is correct
3. Re-run `register-url-scheme-windows.bat`

### Linux: Links don't open the app
1. Verify MIME type association:
   ```bash
   xdg-mime query default x-scheme-handler/selladomx
   ```
   Should return `com.selladomx.SelladoMX.desktop` (Flatpak) or `selladomx.desktop`
2. Check that the desktop file it names exists and has a correct `Exec` line
3. Re-run registration:
   ```bash
   python scripts/test_url_scheme.py
   ```

### macOS: Links don't work
1. Ensure you're running from the .app bundle (not the raw executable)
2. Check Info.plist contains `CFBundleURLTypes`
3. Rebuild the .app with `make build`

## Security Considerations

- Only `selladomx://auth?token=XXX` URLs are accepted
- Token must match `^smx_[A-Za-z0-9]{5,}$` (`SelladoMXAPIClient.validate_token_format`)
- Invalid URLs are logged and rejected silently
- The token is saved only after the API accepts it (balance request)

## Implementation Details

- `src/selladomx/utils/platform_helpers.py`: per-platform registration and checks
- `src/selladomx/utils/deep_link_handler.py`: URL parsing and token validation
- `src/selladomx/main.py`: first-launch registration; links passed as `argv[1]`, via macOS `FileOpen` events, or forwarded from a second instance to the running one over `QLocalServer`

## For Developers

```bash
poetry run selladomx "selladomx://auth?token=smx_test123"
```
