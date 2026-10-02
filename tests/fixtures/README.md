# Test Fixtures

Used by `tests/test_e2e_signing.py` (tests are skipped if `certs/test_cert.cer` or `pdfs/sample.pdf` is missing):

- `certs/test_cert.cer` and `certs/test_key.key` (unencrypted key; the test uses an empty password)
- `pdfs/sample.pdf` (any PDF)

## Test Certificates

Do not commit real e.firma certificates. `certs/.gitignore` excludes all certificate and key files except `test_*` and `dummy_*` `.cer`/`.key`.

Generate a self-signed test certificate:

```bash
openssl req -x509 -newkey rsa:2048 -keyout tests/fixtures/certs/test_key.key \
  -out tests/fixtures/certs/test_cert.cer -days 365 -nodes \
  -subj "/CN=Test Certificate/O=SelladoMX/C=MX"
```
