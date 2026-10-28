# Test Fixtures

`tests/test_e2e_signing.py` does not need files here: `tests/conftest.py` generates a test e.firma (CA-issued certificate with a SAT-like subject, DER `.cer`, PKCS#8 DER `.key` encrypted with a password) and a small PDF in a temporary directory for each test session.

## Test Certificates

Do not commit real e.firma certificates. `certs/.gitignore` excludes all certificate and key files except `test_*` and `dummy_*` `.cer`/`.key`.
