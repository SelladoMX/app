# SelladoMX

[![Build](https://github.com/SelladoMX/app/actions/workflows/build.yml/badge.svg)](https://github.com/SelladoMX/app/actions/workflows/build.yml)
[![CodeQL](https://github.com/SelladoMX/app/actions/workflows/codeql.yml/badge.svg)](https://github.com/SelladoMX/app/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Firma documentos PDF con tu e.firma del SAT directamente desde tu computadora.

## Características

- **Firma PAdES** compatible con Adobe Reader y validadores oficiales
- **Sellado de tiempo (TSA)** básico o profesional con validez legal
- **100% local** - tus documentos nunca salen de tu equipo
- **Validación completa** de certificados (OCSP/CRL)
- **Firma por lotes** - procesa múltiples PDFs a la vez
- **Token management** - comparte acceso con tu equipo

## Seguridad

No guardamos tus documentos, certificados ni contraseñas. Todo el proceso de firma ocurre en tu computadora. Solo nos conectamos a servidores externos para:

- Validación de certificados (OCSP/CRL estándar)
- Sellado de tiempo TSA (opcional)
- Gestión de créditos (solo si usas TSA profesional)

Para reportar vulnerabilidades, consulta [SECURITY.md](SECURITY.md).

## Instalación

### Linux

[![Disponible en Flathub](https://flathub.org/assets/badges/flathub-badge-en.svg)](https://flathub.org/apps/com.selladomx.SelladoMX)

```bash
flatpak install flathub com.selladomx.SelladoMX
flatpak run com.selladomx.SelladoMX
```

También disponible como bundle `.flatpak` en [GitHub Releases](https://github.com/SelladoMX/app/releases).

### macOS

Descarga `SelladoMX-macOS.dmg` desde [GitHub Releases](https://github.com/SelladoMX/app/releases).

### Windows

Descarga `SelladoMX-Windows.zip` desde [GitHub Releases](https://github.com/SelladoMX/app/releases).

### Verificación de descargas

Cada release incluye un archivo `SHA256SUMS.txt` y attestations de GitHub para verificar la integridad de tu descarga:

```bash
# Verificar checksum
sha256sum -c SHA256SUMS.txt

# Verificar procedencia del build (requiere GitHub CLI)
gh attestation verify <archivo-descargado> --repo SelladoMX/app
```

## Uso Rápido

1. **Selecciona PDFs** - arrastra o busca los documentos a firmar
2. **Carga tu certificado** - archivo `.cer` y `.key` de tu e.firma
3. **Firma** - elige TSA básico o profesional y procesa

Los archivos firmados se guardan con el sufijo `_firmado.pdf`.

## TSA Profesional

El TSA básico funciona bien para uso personal. Si necesitas validez legal certificada para trámites oficiales o juicios, usa TSA Profesional:

- Certificación oficial RFC 3161
- Cumplimiento NOM-151-SCFI-2016 y normas europeas eIDAS
- Proveedor europeo certificado
- Evidencia admisible en procesos legales
- Desde $2 MXN por documento

Configura tu token desde **Configuración** o usa un magic link desde tu email.

## Para Desarrolladores

```bash
# Clonar e instalar
git clone https://github.com/SelladoMX/app.git
cd app
poetry install

# Ejecutar en desarrollo
poetry run python run.py

# Ejecutar tests
poetry run pytest

# Construir ejecutables
./scripts/build.sh
```

Requiere Python 3.11+ y Poetry.

### Configuración de Entorno

**Desarrollo local (por defecto):**
```bash
poetry run python run.py
```
Usa automáticamente `.env.development` con `http://localhost:8000`

**Para override personalizado:**
```bash
# Crea tu propio .env (opcional)
echo "SELLADOMX_API_URL=http://localhost:3000" > .env
```

**Builds/Producción:**
Los ejecutables usan los valores hardcodeados con `https://api.selladomx.com`

**Variables disponibles:**
- `SELLADOMX_API_URL` - URL de la API
- `SELLADOMX_DEBUG` - Logging detallado (0 o 1)

## Tecnologías

- **UI**: PySide6 (Qt 6) con QML
- **Firma PDF**: pyhanko
- **Criptografía**: cryptography
- **Validación**: pyhanko-certvalidator
- **TSA básico**: DigiCert/Sectigo/FreeTSA
- **TSA profesional**: Certum eIDAS

## Documentación

- [URL Scheme Registration](docs/URL_SCHEME_REGISTRATION.md) - Deep links y magic links
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Detalles de implementación

## Licencia

[MIT](LICENSE) - usa, modifica y distribuye libremente.

---

**¿Dudas?** Abre un [issue](https://github.com/SelladoMX/app/issues) o escribe a soporte@selladomx.com
