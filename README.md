# SelladoMX

Firma documentos PDF con tu e.firma del SAT directamente desde tu computadora.

## Características

- **Firma PAdES** compatible con Adobe Reader y validadores oficiales
- **Sellado de tiempo (TSA)** gratuito o profesional con validez legal
- **100% local** - tus documentos nunca salen de tu equipo
- **Validación completa** de certificados (OCSP/CRL)
- **Firma por lotes** - procesa múltiples PDFs a la vez
- **Token management** - comparte acceso con tu equipo

## Seguridad

No guardamos tus documentos, certificados ni contraseñas. Todo el proceso de firma ocurre en tu computadora. Solo nos conectamos a servidores externos para:

- Validación de certificados (OCSP/CRL estándar)
- Sellado de tiempo TSA (opcional)
- Gestión de créditos (solo si usas TSA profesional)

## Instalación

Descarga el ejecutable para tu sistema operativo desde [Releases](https://github.com/selladomx/client/releases).

- **Windows**: `SelladoMX.exe` (portable, no requiere instalación)
- **macOS**: `SelladoMX.app` (arrastra a Aplicaciones)
- **Linux**: `SelladoMX.AppImage` (dale permisos de ejecución)

## Uso Rápido

1. **Selecciona PDFs** - arrastra o busca los documentos a firmar
2. **Carga tu certificado** - archivo `.cer` y `.key` de tu e.firma
3. **Firma** - elige TSA gratuito o profesional y procesa

Los archivos firmados se guardan con el sufijo `_firmado.pdf`.

## TSA Profesional

El TSA gratuito funciona bien para uso personal. Si necesitas validez legal garantizada para trámites oficiales o juicios, usa TSA Profesional:

- ✓ Certificación oficial RFC 3161
- ✓ Cumplimiento NOM-151-SCFI-2016
- ✓ Evidencia admisible en procesos legales
- ✓ Desde $2 MXN por documento

Configura tu token desde **Configuración** o usa un magic link desde tu email.

## Para Desarrolladores

```bash
# Clonar e instalar
git clone https://github.com/selladomx/client.git
cd client
poetry install

# Ejecutar en desarrollo
poetry run python run.py

# Construir ejecutables
./scripts/build.sh
```

Requiere Python 3.11+ y Poetry.

### Configuración de Entorno

**Desarrollo local (por defecto):**
```bash
poetry run python run.py
```
Usa automáticamente `.env.development` → `http://localhost:8000`

**Para override personalizado:**
```bash
# Crea tu propio .env (opcional)
echo "SELLADOMX_API_URL=http://localhost:3000" > .env
```

**Builds/Producción:**
Los ejecutables usan los valores hardcodeados → `https://api.selladomx.com`

**Variables disponibles:**
- `SELLADOMX_API_URL` - URL de la API
- `SELLADOMX_DEBUG` - Logging detallado (0 o 1)

## Tecnologías

- **UI**: PySide6 (Qt 6)
- **Firma PDF**: pyhanko
- **Criptografía**: cryptography
- **Validación**: pyhanko-certvalidator
- **TSA gratuito**: DigiCert/Sectigo/FreeTSA
- **TSA profesional**: Certum eIDAS

## Documentación

- [URL Scheme Registration](docs/URL_SCHEME_REGISTRATION.md) - Deep links y magic links
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Detalles de implementación

## Licencia

MIT - usa, modifica y distribuye libremente.

---

**¿Dudas?** Abre un issue o escribe a soporte@selladomx.com
