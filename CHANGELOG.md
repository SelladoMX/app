# Changelog

All notable changes to SelladoMX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-02-11

### Added
- Certificate path persistence - certificate and key paths are now remembered between sessions
- Environment-based API configuration via `.env` file support
- `.env.development` auto-loaded in local development (no need to copy)
- Custom application icon from selladomx.com (replaces default placeholder)
- Icon generation script for all platforms (macOS .icns, Windows .ico, Linux .png)
- Complete design token system for consistent UI styling
- Comprehensive error hover/active states for buttons
- Test fixtures structure for integration testing
- End-to-end signing tests
- CI/CD test job that runs before build

### Changed
- **Migrated UI from QtWidgets to QML/Qt Quick** for better performance and modern UI capabilities
- Refactored `SigningWorker` to dedicated module (`signing/worker.py`)
- Improved design token consistency across all UI components
- Updated README with environment configuration documentation

### Removed
- Deleted `main_window_legacy.py` (unused legacy code)
- Deleted deprecated `colors.py` (replaced by `design_tokens.py`)
- Removed unused `QTimer` import

### Fixed
- Hardcoded API URLs replaced with environment variables
- All hardcoded hex colors replaced with design tokens
- Fixed Qt library dependencies for Linux CI/CD builds
- Updated test suite to work with new TSA client architecture

## [0.1.0] - TBD

### Added
- Initial public release
- PDF signing with e.firma certificates
- Free TSA support (DigiCert, Sectigo, FreeTSA)
- Professional TSA support with credit system
- Token management (primary and derived tokens)
- Deep link support for token configuration (`selladomx://`)
- Certificate validation (OCSP/CRL)
- Cross-platform support (macOS, Windows, Linux)
- Onboarding tutorial
- Professional design system with light theme

### Features
- 3-step guided workflow
- Real-time certificate validation
- Background signing (non-blocking UI)
- Credit balance tracking
- Token expiration warnings
- Output directory selection
- Multiple PDF batch signing
- Token management dialog
- API key configuration

### Security
- OS-level encrypted token storage via QSettings
- Certificate validation before signing
- Token format validation
- Private key security (cleared on app close)
- No document upload - all processing local

### Developer Experience
- Poetry-based dependency management
- PyInstaller build system
- CI/CD pipeline for all platforms
- Comprehensive error handling
- Structured logging

---

## Release Notes Template

When preparing a new release:

1. Update version in `pyproject.toml`
2. Update version in `src/selladomx/main.py`
3. Move Unreleased changes to new version section
4. Add release date
5. Create git tag: `git tag v0.1.0`
6. Push tag: `git push origin v0.1.0`
7. CI/CD will automatically build and create GitHub release
