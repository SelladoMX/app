# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in SelladoMX, please report it responsibly:

1. **Do NOT open a public issue.** Security vulnerabilities should not be disclosed publicly until a fix is available.
2. **Email:** Send details to **soporte@selladomx.com** with the subject "Security Vulnerability Report".
3. **Include:** A description of the vulnerability, steps to reproduce, and potential impact.

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Scope

The following are in scope for security reports:

- The SelladoMX desktop application (this repository)
- Certificate handling and private key protection
- PDF signing integrity
- Network communications (API, TSA, OCSP/CRL)
- Local data storage and settings

## Security Architecture

- **Local processing:** PDF signing happens entirely on the user's machine. Documents are never uploaded to external servers.
- **Certificate handling:** Private keys (.key files) are loaded into memory only during signing, never stored by the application.
- **Network connections:** Limited to certificate validation (OCSP/CRL), TSA timestamping, and optional credit management API.
- **Settings storage:** API tokens are stored via QSettings (OS-encrypted storage). No passwords are persisted.

## Verification

All release artifacts include SHA256 checksums and GitHub build attestations. To verify a download:

```bash
# Verify checksum
sha256sum -c SHA256SUMS.txt

# Verify build provenance (requires GitHub CLI)
gh attestation verify <downloaded-file> --repo SelladoMX/app
```
