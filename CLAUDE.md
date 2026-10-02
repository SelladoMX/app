# SelladoMX client

Desktop app that signs PDFs (PAdES) with a SAT e.firma (`.cer` + `.key`) and adds an RFC 3161 timestamp. Python 3.11–3.13, PySide6 with a QML UI, pyhanko for signing.

## Commands

```bash
poetry install --with dev
poetry run selladomx               # run (or: make run)
poetry run pytest -m "not network" # tests that don't hit real TSAs
poetry run black src tests         # formatter (line length 88); no linter is configured
make build                         # PyInstaller build for the current OS (cleans first)
make reset-onboarding              # show the first-run onboarding again
```

`make help` lists the rest. Linux is shipped only as a Flatpak; the offline Flatpak build is in `docs/developer/packaging.md`.

## Layout

- `src/selladomx/main.py`: entry point. Enforces a single instance (`QLocalServer`), handles `selladomx://` deep links, and exposes the view models to QML as context properties.
- `src/selladomx/ui/qml/`: the UI. `design/DesignTokens.qml` is a singleton holding colors, spacing and sizes.
- `src/selladomx/ui/qml_bridge/`: `QObject` view models for QML. `MainViewModel` holds the three-step state (files → certificate → sign).
- `src/selladomx/signing/`: certificate loading, PDF signing and TSA clients. Only `worker.py` imports PySide6.
- `src/selladomx/api/`: HTTP client for the SelladoMX API (credits, professional timestamps, history, tokens).
- `src/selladomx/utils/`: QSettings wrapper, deep links, URL-scheme registration, update check.
- `src/selladomx/config.py`: constants and environment variables.

## Things the code doesn't make obvious

- `config.py` reads env vars at import time. `main.py` calls `load_dotenv()` (falling back to `.env.development`) before importing anything that imports `config`. Keep that order.
- Free timestamps go directly to the TSAs in `TSA_FREE_PROVIDERS`. Professional timestamps go through the API (`APITimeStamper`), which forwards to Certum. Each signed document costs one credit.
- QSettings (`QSettings("SelladoMX", "SelladoMX")`) stores the API token in plaintext. Never log or display the full token.
- The `COLOR_*` constants in `config.py` must match `DesignTokens.qml`.
- The version appears in `pyproject.toml`, `src/selladomx/__init__.py`, `selladomx.spec` (`CFBundle*Version`) and `com.selladomx.SelladoMX.metainfo.xml`. The release checklist is in `docs/developer/packaging.md`.
- User-facing strings are in Spanish; log messages are in English. The docs are in Spanish.
- CI (`.github/workflows/build.yml`) runs on `v*` tags and manual dispatch. It builds the Windows zip, the macOS DMG and the Flatpak bundle, with build-provenance attestations.

## Comments and docs

Write a comment only when it tells the reader something the code can't: an ordering constraint, a workaround, a security boundary, or the reason for a non-obvious choice, stated once. Don't narrate steps, label self-describing elements, record history ("now", "used to"), or describe plans; put plans in issues. Keep docstrings (including Args/Returns), `# ====` banners in long files, and QML landmarks on containers without an id. Check doc claims against the code before writing them.
