# Test Fixtures

This directory contains test assets for integration testing.

## Structure

- `certs/` - Test certificates and private keys
- `pdfs/` - Sample PDF files for signing tests

## Test Certificates

For security reasons, **DO NOT commit real e.firma certificates** to this repository.

Use one of the following approaches:

1. **Generate self-signed test certificates** (recommended for CI/CD):
   ```bash
   # Generate test certificate
   openssl req -x509 -newkey rsa:2048 -keyout tests/fixtures/certs/test_key.key \
     -out tests/fixtures/certs/test_cert.cer -days 365 -nodes \
     -subj "/CN=Test Certificate/O=SelladoMX/C=MX"
   ```

2. **Use expired/revoked certificates** from public test data

3. **Store real certificates locally** (excluded from git via .gitignore)
   - Tests will be skipped if certificates are not available
   - Good for local development with real signing

## Sample PDFs

Add a simple test PDF to `pdfs/sample.pdf` for testing. You can create one with:

```bash
# Create a simple test PDF
echo "This is a test document for PDF signing." > test.txt
# Convert to PDF (requires tools like pandoc, wkhtmltopdf, etc.)
```

Or use any existing PDF file.
